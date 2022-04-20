class NestedKwargsMixin(object):
    def get_serializer_context(self):
        context = super(NestedKwargsMixin, self).get_serializer_context()
        context.update(dict(
            kwargs=self.get_parents_query_dict()
        ))
        return context
