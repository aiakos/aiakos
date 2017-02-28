from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def password_change(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)

		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password has been successfully updated!')
			return redirect('custom-password-change')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'registration/password_change.html', {
		'form': form,
	})


def password_reset(request):
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)

		if form.is_valid():
			email = form.cleaned_data['email']

			try:
				user = User.objects.get(email=email)
			except User.DoesNotExist:
				messages.success(request, 'Check your e-mail.')
				return redirect('custom-password-reset')
			else:
				if user.can_reset_password:
					form.save(
						request=request,
					)
					messages.success(request, 'Check your e-mail.')
					return redirect('custom-password-reset')
				else:
					messages.warning(request, 'You already have an account; log in with: ... TODO')
					return redirect('custom-password-reset')
	else:
		form = PasswordResetForm()

	return render(request, 'registration/password_reset.html', {
		'form': form,
	})
