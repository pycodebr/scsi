from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Notification


class UnreadCountView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(
            brokerage=request.tenant,
            user=request.user,
            is_read=False,
        ).count()
        return JsonResponse({'count': count})


@method_decorator(csrf_exempt, name='dispatch')
class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user,
            brokerage=request.tenant,
        )
        notif.is_read = True
        notif.save(update_fields=['is_read', 'updated_at'])
        return JsonResponse({'ok': True})


class ListNotificationsView(LoginRequiredMixin, View):
    def get(self, request):
        notifs = Notification.objects.filter(
            brokerage=request.tenant,
            user=request.user,
        ).order_by('-created_at')[:20]
        data = [
            {
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'message': n.message,
                'url': n.url,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifs
        ]
        return JsonResponse(data, safe=False)