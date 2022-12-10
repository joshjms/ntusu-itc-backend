from rest_framework import generics


class CompleteAPIView(
        generics.mixins.RetrieveModelMixin,
        generics.mixins.CreateModelMixin,
        generics.mixins.UpdateModelMixin,
        generics.mixins.DestroyModelMixin,
        generics.mixins.ListModelMixin,
        generics.GenericAPIView):
    """
        Concrete view that provides:
        list and create view if lookup field is not provided,
        detail view, update, delete if lookup field is provided
    """
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get(self.lookup_field, None)
        return (
            self.retrieve(request, *args, **kwargs) if pk
            else self.list(request, *args, **kwargs)
        )
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
