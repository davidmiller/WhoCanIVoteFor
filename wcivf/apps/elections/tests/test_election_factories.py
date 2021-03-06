from django.test import TestCase

from elections.tests.factories import (
    ElectionFactory, PostFactory, VotingSystemFactory)

from elections.models import Election, Post, VotingSystem

class TestFactories(TestCase):
    """
    Meta tests to ensure that the factories are working
    """

    def _test_save(self, model, factory):
        self.assertEqual(model.objects.all().count(), 0)
        created_model = factory.create()
        self.assertEqual(model.objects.all().count(), 1)
        return created_model

    def test_election_factory(self):
        model = self._test_save(Election, ElectionFactory)
        self.assertEqual(model.name, "UK General Election 2015")

    def test_post_factory(self):
        model = self._test_save(Post, PostFactory)
        self.assertEqual(model.label, "copeland")

    def test_voting_system_factory(self):
        model = self._test_save(VotingSystem, VotingSystemFactory)
        self.assertEqual(model.name, "First Past The Post")
