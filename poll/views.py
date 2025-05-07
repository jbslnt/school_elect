from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponseRedirect
from .forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Candidate, ControlVote, Position, UserVote, UserProfile, ElectionEvent
from django.utils.timezone import localtime
from django.utils import timezone
from .forms import EditProfileForm
from collections import defaultdict
from django.utils.timezone import now
from django.db.models import Count
import json


def homeView(request):
    return render(request, "poll/home.html")

def registrationView(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            if User.objects.filter(email=cd['email']).exists():
                form.add_error('email', 'Email is already registered.')
                return render(request, "poll/registration.html", {'form': form})
            
            if cd['password'] == cd['confirm_password']:
                user = form.save(commit=False)
                user.set_password(cd['password'])
                user.save()

                # ✅ Now the UserProfile will be created via signal or OneToOne
                profile = user.userprofile
                profile.gender = cd['gender']
                profile.program = cd['program']
                profile.department = cd['department']
                profile.year = cd['year']
                profile.student_id = cd['student_id']
                profile.save()

                messages.success(request, 'You have been registered.')
                return redirect('home')
            else:
                return render(request, "poll/registration.html", {'form': form, 'note': 'password must match'})
    else:
        form = RegistrationForm()

    return render(request, "poll/registration.html", {'form': form})


def loginView(request):
    # If the user is already authenticated, redirect to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            
            # Check if the email ends with '@jmc.edu.ph'
            if not email.endswith('@jmc.edu.ph'):
                messages.error(request, 'Only emails under @jmc.edu.ph are allowed.')
                return render(request, "poll/login.html")
            
            # Authenticate the user
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password!')
            return render(request, "poll/login.html")
    else:
        return render(request, "poll/login.html")



@login_required
def logoutView(request):
    logout(request)
    return redirect('home')


@login_required
def dashboardView(request):
    events = ElectionEvent.objects.all()

    if request.method == 'POST':
        selected_event_id = request.POST.get('selected_event')
        if selected_event_id:
            request.session['selected_event_id'] = int(selected_event_id)
            return redirect('dashboard')

    selected_event_id = request.session.get('selected_event_id')
    current_event = ElectionEvent.objects.filter(id=selected_event_id).first() if selected_event_id else None

    if current_event:
        positions = Position.objects.filter(event=current_event)
        total_voters = ControlVote.objects.filter(position__in=positions, status=True).values('user').distinct().count()
        total_users = User.objects.count()  # Or filter by event if needed
        turnout = round((total_voters / total_users) * 100, 2) if total_users else 0
        event_status = current_event.status()
        
        # Filter UserProfile by the selected event and their related data
        users_for_event = UserProfile.objects.filter(user__controlvote__position__event=current_event)
    else:
        total_users = 0
        total_voters = 0
        turnout = 0
        event_status = "No event selected"
        users_for_event = UserProfile.objects.none()  # No users if no event is selected

    # Demographics filtered by the selected event
    gender_stats = users_for_event.values('gender').annotate(count=Count('gender'))
    program_stats = users_for_event.values('program').annotate(count=Count('program'))
    year_stats = users_for_event.values('year').annotate(count=Count('year'))
    department_stats = users_for_event.values('department').annotate(count=Count('department'))

    profile = request.user.userprofile
    show_terms = not profile.accepted_terms

    # Prepare the chart data for JSON serialization
    context = {
        'total_users': total_users,
        'total_voters': total_voters,
        'turnout': turnout,
        'events': events,
        'event': current_event,
        'event_status': event_status,
        'show_terms': show_terms,
        'selected_event_id': selected_event_id,
        'gender_stats': gender_stats,
        'program_stats': program_stats,
        'year_stats': year_stats,
        'department_stats': department_stats,
    }

    context.update({
        'gender_labels': json.dumps([entry['gender'] for entry in gender_stats]),
        'gender_counts': json.dumps([entry['count'] for entry in gender_stats]),
        'year_labels': json.dumps([entry['year'] for entry in year_stats]),
        'year_counts': json.dumps([entry['count'] for entry in year_stats]),
        'program_labels': json.dumps([entry['program'] for entry in program_stats]),
        'program_counts': json.dumps([entry['count'] for entry in program_stats]),
        'department_labels': json.dumps([entry['department'] for entry in department_stats]),
        'department_counts': json.dumps([entry['count'] for entry in department_stats]),
    })

    return render(request, "poll/dashboard.html", context)


@login_required
def positionView(request):
    # Get selected election from session
    selected_event_id = request.session.get('selected_event_id')
    selected_event = ElectionEvent.objects.filter(id=selected_event_id).first()

    if not selected_event:
        # Show modal message if no election is selected
        context = {
            'obj': [],
            'show_event_modal': True,
            'modal_message': "No election event selected. Please select one from your dashboard."
        }
        return render(request, "poll/position.html", context)

    # Fetch positions for the selected event
    positions = Position.objects.filter(event=selected_event)

    context = {
        'obj': positions,
        'show_event_modal': False,
    }

    return render(request, "poll/position.html", context)


    
@login_required
def candidateView(request, pos):
    # Get selected event from session
    selected_event_id = request.session.get('selected_event_id')
    current_event = ElectionEvent.objects.filter(id=selected_event_id).first()

    if not current_event:
        messages.error(request, "No election event selected.")
        return redirect('dashboard')

    # Get all positions for the event and determine navigation order
    positions = list(Position.objects.filter(event=current_event).order_by('id'))
    obj = get_object_or_404(Position, pk=pos, event=current_event)

    try:
        current_index = positions.index(obj)
        prev_position = positions[current_index - 1].id if current_index > 0 else None
        next_position = positions[current_index + 1].id if current_index < len(positions) - 1 else None
    except ValueError:
        prev_position = next_position = None

    # Ensure the user accepted terms
    if not request.user.userprofile.accepted_terms:
        return redirect('accept_terms')

    event_active = current_event.is_active()

    if request.method == "POST":
        if not event_active:
            return render(request, 'poll/candidate.html', {
                'obj': obj,
                'event': current_event,  # Pass the event to the template
                'event_status': current_event.status(),
                'can_vote': False,
                'show_vote_disabled_modal': True,
                'prev_position': prev_position,
                'next_position': next_position
            })

        control_vote, _ = ControlVote.objects.get_or_create(user=request.user, position=obj)

        if not control_vote.status:
            candidate_id = request.POST.get("candidate")
            candidate = get_object_or_404(Candidate, pk=candidate_id, position=obj)

            UserVote.objects.create(user=request.user, candidate=candidate)
            candidate.total_vote += 1
            candidate.save()

            control_vote.status = True
            control_vote.save()

            messages.success(request, f"You successfully voted for {candidate.name} as {candidate.position}.")
            return redirect('candidate', next_position) if next_position else redirect('position')
        else:
            messages.error(request, 'You have already voted for this position.')

    return render(request, 'poll/candidate.html', {
        'obj': obj,
        'event': current_event,  # Pass the event to the template here too
        'event_status': current_event.status(),
        'can_vote': event_active,
        'show_vote_disabled_modal': not event_active,
        'prev_position': prev_position,
        'next_position': next_position
    })



@login_required
def acceptTermsView(request):
    profile = request.user.userprofile
    profile.accepted_terms = True
    profile.save()
    return redirect('dashboard')



@login_required
def candidateDetailView(request, id):
    obj = get_object_or_404(Candidate, pk=id)
    return render(request, "poll/candidate_detail.html", {'obj':obj})


@login_required
def changePasswordView(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "poll/password.html", {'form':form})


@login_required
def editProfileView(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user, user=user)
        if form.is_valid():
            user = form.save()

            # Update UserProfile fields
            profile = user.userprofile
            profile.gender = form.cleaned_data['gender']
            profile.program = form.cleaned_data['program']
            profile.department = form.cleaned_data['department']
            profile.year = form.cleaned_data['year']
            profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = EditProfileForm(instance=user, user=user)

    return render(request, "poll/edit_profile.html", {'form': form})

@login_required
def adminDashboardView(request):
    if not request.user.is_staff:
        return render(request, 'poll/no_access.html') 

    # Existing dashboard logic here
    positions = Position.objects.all()
    summary = []

    for pos in positions:
        candidates = Candidate.objects.filter(position=pos)
        candidate_votes = []
        for candidate in candidates:
            vote_count = UserVote.objects.filter(candidate=candidate).count()
            candidate_votes.append({
                'name': candidate.name,
                'votes': vote_count,
                'partylist': candidate.partylist
            })
        summary.append({'position': pos.title, 'candidates': candidate_votes})

    return render(request, 'poll/admin_dashboard.html', {'summary': summary})


@login_required
def myBallotView(request):
    selected_event_id = request.session.get('selected_event_id')

    if not selected_event_id:
        messages.error(request, "No election event selected.")
        return redirect('dashboard')

    event = get_object_or_404(ElectionEvent, id=selected_event_id)

    # Filter votes for the current user and the selected event
    votes = UserVote.objects.filter(
        user=request.user,
        candidate__position__event=event
    ).select_related('candidate', 'candidate__position')

    return render(request, 'poll/my_ballot.html', {
        'votes': votes,
        'event_name': event.title
    })



@login_required
def resultView(request):
    selected_event_id = request.session.get('selected_event_id')
    current_event = ElectionEvent.objects.filter(id=selected_event_id).first()

    if not current_event:
        return render(request, "poll/result.html", {
            'show_modal': True,
            'modal_message': "There is no ongoing election at the moment.",
        })

    if not current_event.has_ended():
        return render(request, "poll/result.html", {
            'show_modal': True,
            'modal_message': "Election results will be available once the election has ended.",
        })

    positions = Position.objects.filter(event=current_event)

    all_candidates = Candidate.objects.filter(position__event=current_event).order_by('position', '-total_vote')

    last_vote = UserVote.objects.filter(candidate__position__event=current_event).order_by('-timestamp').first()
    last_updated = localtime(last_vote.timestamp) if last_vote else None

    results = defaultdict(list)
    for pos in positions:
        candidates = Candidate.objects.filter(position=pos).order_by('-total_vote')
        total_votes = sum(c.total_vote for c in candidates) or 1

        for idx, candidate in enumerate(candidates):
            percentage = (candidate.total_vote / total_votes) * 100
            is_winner = idx == 0 and candidate.total_vote > 0
            results[pos.title].append({
                'candidate': candidate,
                'percentage': round(percentage, 2),
                'status': 'Winner' if is_winner else 'Participant'
            })

    return render(request, "poll/result.html", {
        'obj': all_candidates,
        'results': dict(results),
        'last_updated': last_updated,
        'show_modal': False,
        'current_event': current_event
    })