from haystack import indexes

from instagram.models import InstagramList


class InstagramListIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #desc = indexes.CharField(model_attr='desc')
    #content = indexes.CharField(model_attr='message')

    def get_model(self):
        return InstagramList

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

