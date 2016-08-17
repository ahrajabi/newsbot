import datetime
from haystack import indexes
from .models import Entity
from hazm import *

normalizer = Normalizer()
stemmer = Stemmer()
lemmatizer = Lemmatizer()
class EntityIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name',boost=0.1,faceted=True)
    wiki_name = indexes.CharField(model_attr='wiki_name',boost=0.9)
    status = indexes.CharField(model_attr='status')
    summary = indexes.CharField(model_attr='summary',boost=5)


    def get_model(self):
        return Entity


    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
