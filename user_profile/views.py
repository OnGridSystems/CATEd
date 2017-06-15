from django.http import HttpResponse
from trade.models import UserExchanges
from django.shortcuts import render


# Create your views here.
def profile(request):
    args = {'user': request.user}
    args['user_exchanges'] = UserExchanges.objects.filter(user=args['user'])
    args['user_active_exchanges'] = args['user_exchanges'].filter(is_active=True)
    if request.POST:
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        if first_name is not None:
            args['user'].first_name = first_name
        if last_name is not None:
            args['user'].last_name = last_name
        if last_name or first_name:
            args['user'].save()
    return render(request, 'user_profile/profile.html', args)
