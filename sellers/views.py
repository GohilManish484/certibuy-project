from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from accounts.decorators import role_required, login_required_custom
from .models import SellerSubmission, SubmissionImage
from .forms import SellerSubmissionForm
import logging

logger = logging.getLogger(__name__)


@role_required('seller', 'customer')
def submit_product(request):
    """Allow both sellers and customers to submit products for verification"""
    if request.method == 'POST':
        form = SellerSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.seller = request.user
                submission.save()
                
                images = request.FILES.getlist('images')
                
                if not images:
                    messages.warning(request, 'No images uploaded. Please add at least one image.')
                    return redirect('sellers:submit_product')
                
                if len(images) > 10:
                    messages.error(request, 'Maximum 10 images allowed per submission.')
                    submission.delete()
                    return redirect('sellers:submit_product')
                
                for image in images:
                    try:
                        SubmissionImage.objects.create(submission=submission, image=image)
                    except ValidationError as e:
                        submission.delete()
                        messages.error(request, f'Image validation failed: {str(e)}')
                        return redirect('sellers:submit_product')
                
                messages.success(request, 'Product submitted successfully! We will review it soon.')
                return redirect('sellers:my_submissions')
                
            except Exception as e:
                logger.error(f'Submission error for user {request.user.id}: {str(e)}')
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('sellers:submit_product')
    else:
        form = SellerSubmissionForm()
    
    return render(request, 'sellers/submit_product.html', {'form': form})

@role_required('seller', 'customer')
def my_submissions(request):
    """View all submissions for the logged-in seller/customer"""
    try:
        submissions = SellerSubmission.objects.filter(
            seller=request.user
        ).prefetch_related('images').order_by('-created_at')
        return render(request, 'sellers/my_submissions.html', {'submissions': submissions})
    except Exception as e:
        logger.error(f'Error fetching submissions for user {request.user.id}: {str(e)}')
        messages.error(request, 'Unable to load submissions.')
        return redirect('core:home')

@login_required_custom
def submission_detail(request, pk):
    """View details of a specific submission (seller/customer can view own, staff can view all)"""
    try:
        submission = get_object_or_404(SellerSubmission, pk=pk)
        
        if not (request.user == submission.seller or request.user.is_staff):
            logger.warning(
                f'Unauthorized access attempt to submission {pk} by user {request.user.id}'
            )
            messages.error(request, 'You do not have permission to view this submission.')
            return render(request, '403.html', status=403)
        
        return render(request, 'sellers/submission_detail.html', {'submission': submission})
    
    except Exception as e:
        logger.error(f'Error viewing submission {pk}: {str(e)}')
        messages.error(request, 'Unable to load submission details.')
        return redirect('sellers:my_submissions')
