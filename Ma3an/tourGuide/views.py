from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Agency, TourGuide
from django.contrib import messages

# Create your views here.


@login_required
def all_tourguides_view(request):

    if request.user.role != 'agency':
        return redirect('accounts:profile')

    agency = request.user.agency_profile
    tour_guides = agency.tour_guides.select_related('user')

    return render(request, 'tourGuide/all_tourGuides.html', {
        'agency': agency,
        'tour_guides': tour_guides,
    })
    

@login_required
def delete_tourguide(request, guide_id):
    if request.user.role != 'agency':
        return redirect('accounts:profile')

    agency = request.user.agency_profile
    guide = get_object_or_404(TourGuide, id=guide_id, agency=agency)

    if request.method == 'POST':
        first_name = guide.user.first_name
        last_name = guide.user.last_name

        guide.user.delete()

        messages.success(
            request,
            f'Tour guide "{first_name} {last_name}" has been deleted successfully.'
        )

    # if request.method == 'POST':
    #     guide.user.delete()
        return redirect('tourGuide:all_tourguides')

    return redirect('tourGuide:all_guides')


