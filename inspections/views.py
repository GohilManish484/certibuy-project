from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import role_required, inspector_required, admin_required
from .models import Inspection
from sellers.models import SellerSubmission
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@role_required('inspector', 'admin')
def inspection_list(request):
    """View inspections: Inspectors see their own, admins see all"""
    try:
        if request.user.role == 'inspector':
            inspections = Inspection.objects.filter(inspector=request.user)
        else:  # admin/staff
            inspections = Inspection.objects.all()
        
        context = {
            'inspections': inspections.select_related('submission', 'inspector')
        }
        return render(request, 'inspections/inspection_list.html', context)
    except Exception as e:
        logger.error(f'Error loading inspections for user {request.user.id}: {str(e)}')
        messages.error(request, 'Unable to load inspections.')
        return redirect('core:home')

@role_required('inspector', 'admin')
def inspection_detail(request, pk):
    """View a specific inspection (inspector can view own, admin can view all)"""
    try:
        inspection = get_object_or_404(Inspection, pk=pk)
        
        # Verify authorization: inspector only sees own inspections, admins see all
        if request.user.role == 'inspector' and request.user != inspection.inspector:
            logger.warning(
                f'Unauthorized inspection access attempt by user {request.user.id} to inspection {pk}'
            )
            messages.error(request, 'You do not have permission to view this inspection.')
            return render(request, '403.html', status=403)
        
        context = {'inspection': inspection}
        return render(request, 'inspections/inspection_detail.html', context)
    except Exception as e:
        logger.error(f'Error loading inspection {pk}: {str(e)}')
        messages.error(request, 'Unable to load inspection details.')
        return redirect('inspections:list')

@admin_required
def create_inspection(request, submission_id):
    """Create a new inspection for a submission (admin only)"""
    submission = get_object_or_404(SellerSubmission, pk=submission_id)
    
    if request.method == 'POST':
        inspector_id = request.POST.get('inspector')
        inspection_date = request.POST.get('inspection_date')
        condition_grade = request.POST.get('condition_grade')
        inspection_notes = request.POST.get('inspection_notes')
        status = request.POST.get('status', 'pending')
        
        inspection = Inspection.objects.create(
            submission=submission,
            inspector_id=inspector_id,
            inspection_date=inspection_date,
            condition_grade=condition_grade,
            inspection_notes=inspection_notes,
            status=status
        )
        
        submission.status = 'inspection_scheduled'
        submission.save()
        
        messages.success(request, 'Inspection created successfully.')
        return redirect('inspections:detail', pk=inspection.pk)
    
    from accounts.models import User
    inspectors = User.objects.filter(role='inspector')
    
    context = {
        'submission': submission,
        'inspectors': inspectors,
    }
    return render(request, 'inspections/create_inspection.html', context)


@inspector_required
def update_inspection(request, pk):
    """Update inspection report (inspector only for assigned inspections)"""
    try:
        inspection = get_object_or_404(Inspection, pk=pk)
        
        # Verify inspector is assigned to this inspection
        if request.user != inspection.inspector:
            logger.warning(
                f'Unauthorized update attempt by user {request.user.id} on inspection {pk}'
            )
            messages.error(request, 'You can only update inspections assigned to you.')
            return render(request, '403.html', status=403)
        
        if request.method == 'POST':
            try:
                inspection.condition_grade = request.POST.get('condition_grade', inspection.condition_grade)
                inspection.inspection_notes = request.POST.get('inspection_notes', inspection.inspection_notes)
                inspection.status = request.POST.get('status', inspection.status)
                
                # If inspection is completed, update submission status
                if inspection.status == 'completed':
                    inspection.submission.status = 'inspection_completed'
                    inspection.submission.save()
                
                inspection.save()
                logger.info(f'Inspection {pk} updated by user {request.user.id}')
                messages.success(request, 'Inspection report updated successfully.')
                return redirect('inspections:detail', pk=inspection.pk)
            
            except Exception as e:
                logger.error(f'Error updating inspection {pk}: {str(e)}')
                messages.error(request, 'Failed to update inspection. Please try again.')
                return redirect('inspections:detail', pk=pk)
        
        context = {'inspection': inspection}
        return render(request, 'inspections/update_inspection.html', context)
    
    except Exception as e:
        logger.error(f'Error accessing inspection {pk} for update: {str(e)}')
        messages.error(request, 'Unable to access inspection.')
        return redirect('inspections:list')
