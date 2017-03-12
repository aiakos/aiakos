from django import forms
from django.contrib import messages
from django.contrib.auth import password_validation, update_session_auth_hash
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _


class SetPasswordForm(forms.Form):
	new_password = forms.CharField(
		label=_("New password"),
		widget=forms.PasswordInput,
		strip=False,
		help_text=password_validation.password_validators_help_text_html(),
	)

	def __init__(self, user, *args, **kwargs):
		self.user = user
		super().__init__(*args, **kwargs)

	def process(self, commit=True):
		password = self.cleaned_data["new_password"]
		self.user.set_password(password)
		if commit:
			self.user.save()
		return self.user


def password_change(request):
	if request.method == 'POST':
		form = SetPasswordForm(request.user, request.POST)

		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password has been successfully updated!')
			return redirect('change-password')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = SetPasswordForm(request.user)
	return render(request, 'registration/password_change.html', {
		'form': form,
	})
