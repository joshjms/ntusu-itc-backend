from rest_framework.generics import GenericAPIView
from rest_framework import mixins


class UpdateDestroyAPIView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
