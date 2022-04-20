from django import forms
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from icmo_users.models import IcmoUser, Referral, Suggestion, SignupLead


class IcmoUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = IcmoUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(IcmoUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class IcmoUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        help_text="<a href=\"password/\">Change Password</a>."
    )

    class Meta:
        model = IcmoUser
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class IcmoUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = IcmoUserChangeForm
    add_form = IcmoUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_active', 'is_admin', 'is_staff', 'is_beta', 'date_joined')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_beta',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', )}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(IcmoUser, IcmoUserAdmin)


# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)


class IcmoReferralAdmin(ModelAdmin):
    list_display = ('email', 'referrer', 'date_sent',)
    list_filter = ('date_sent',)
    search_fields = ('email', 'referrer__email')
    ordering = ('date_sent', 'email',)
    filter_horizontal = ()


admin.site.register(Referral, IcmoReferralAdmin)


class IcmoSuggestionAdmin(ModelAdmin):
    list_display = ('user', 'date_sent',)
    list_filter = ('date_sent',)
    search_fields = ('user__email',)
    ordering = ('date_sent', 'user',)
    filter_horizontal = ()


class SignupLeadAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company_name', 'created', 'modified')
    search_fields = ('email', 'company_name')
    order = ('-modified', '-created')


admin.site.register(SignupLead, SignupLeadAdmin)

admin.site.register(Suggestion, IcmoSuggestionAdmin)
