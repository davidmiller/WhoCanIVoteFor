import re

from icalendar import Calendar, Event, vText

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.core.cache import cache

from .mixins import (ElectionNotificationFormMixin, LogLookUpMixin,
                     PostcodeToPostsMixin, PollingStationInfoMixin)
from people.models import PersonPost


class PostcodeView(ElectionNotificationFormMixin, PostcodeToPostsMixin,
                   PollingStationInfoMixin, LogLookUpMixin, TemplateView):
    """
    This is the main view that takes a postcode and shows all elections
    for that area, with related information.

    This is really the main destination page of the whole site, so there is a
    high chance this will need to be split out in to a few mixins, and cached
    well.
    """
    template_name = 'elections/postcode_view.html'

    def postelections_to_people(self, postelection):
        key = "person_posts_{}".format(postelection.post.ynr_id)
        people_for_post = cache.get(key)
        if people_for_post:
            return people_for_post

        people_for_post = PersonPost.objects.filter(
            post=postelection.post,
            election=postelection.election
            )
        people_for_post = people_for_post.select_related('person')

        if postelection.election.uses_lists:
            order_by = ['party__party_name', 'list_position']
        else:
            order_by = ['person__name']

        people_for_post = people_for_post.order_by(*order_by)
        people_for_post = people_for_post.select_related('post')
        people_for_post = people_for_post.select_related('election')
        cache.set(key, people_for_post)
        return people_for_post


    def clean_postcode(self, postcode):
        incode_pattern = '[0-9][ABD-HJLNP-UW-Z]{2}'
        space_regex = re.compile(r' *(%s)$' % incode_pattern)
        postcode = space_regex.sub(r' \1', postcode.upper())
        return postcode

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.postcode = self.clean_postcode(kwargs['postcode'])
        context['postcode'] = self.postcode
        self.log_postcode(context['postcode'])
        context['postelections'] = self.postcode_to_posts(context['postcode'])
        context['people_for_post'] = {}
        for postelection in context['postelections']:
            postelection.people = self.postelections_to_people(postelection)

        context['polling_station'] = self.get_polling_station_info(
            context['postcode'])

        # #Always add the EU Ref for the time being
        # try:
        #     eu_ref = Election.objects.get(slug='ref.2016-06-23')
        #     context['elections'] = list(context['elections'])
        #     context['elections'].append(eu_ref)
        # except Election.DoesNotExist:
        #     pass

        return context


class PostcodeiCalView(PostcodeToPostsMixin, View,
                       PollingStationInfoMixin):

    def get(self, request, *args, **kwargs):
        postcode = kwargs['postcode']
        polling_station = self.get_polling_station_info(postcode)

        cal = Calendar()
        cal['summary'] = 'Elections in {}'.format(postcode)
        cal['X-WR-CALNAME'] = 'Elections in {}'.format(postcode)
        cal['X-WR-TIMEZONE'] = 'Europe/London'

        cal.add('version', '2.0')
        cal.add('prodid', '-//Elections in {}//mxm.dk//'.format(postcode))
        for post in self.postcode_to_posts(postcode):
            event = Event()
            event['uid'] = "{}-{}".format(post.ynr_id, post.election.slug)
            event['summary'] = "{} - {}".format(post.election.name, post.label)


            event.add('dtstart', post.election.start_time)
            event.add('dtend', post.election.end_time)
            event.add('DESCRIPTION', "Find out more at {}/elections/{}/".format(
                settings.CANONICAL_URL,
                postcode
            ))

            if polling_station['polling_station_known']:
                event['geo'] = "{};{}".format(
                    polling_station['polling_station']['location']['latitude'],
                    polling_station['polling_station']['location']['longitude'],
                )
                event['location'] = vText("{}, {}".format(
                    polling_station['polling_station']['address'].replace('\n', ', '),
                    polling_station['polling_station']['postcode'],
                ))

            cal.add_component(event)

        return HttpResponse(
            cal.to_ical(),
            content_type="text/calendar"
            )
