import uuid
import logging

from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import login, get_user_model
from django.contrib import messages

from .forms import RegisterPhoneForm, LoginPhoneForm, VerifyOTPForm
from .models import Profile, OTPCode
from .services import (
    generate_otp_code,
    send_otp_sms,
    can_request_otp,
    check_ip_rate_limit,
    check_daily_otp_limit,
    OTPSendError,
)

User = get_user_model()
logger = logging.getLogger(__name__)


def _issue_otp(request, form, phone_number):
    """
    Shared "send me a code" flow used by both register and login.
    Returns True and creates the OTPCode row only if the SMS actually went
    out - if Kavenegar fails, nothing is persisted so the person isn't stuck
    behind the 120s cooldown for a code they never received.
    On failure, appends the right error to `form` and returns False.
    """
    if not check_ip_rate_limit(request):
        form.add_error(None, 'تعداد درخواست‌های شما بیش از حد مجاز است. کمی بعد تلاش کنید.')
        return False

    if not can_request_otp(phone_number):
        form.add_error(None, 'لطفاً کمی صبر کنید و دوباره تلاش کنید.')
        return False

    if not check_daily_otp_limit(phone_number):
        form.add_error(None, 'تعداد درخواست‌های امروز برای این شماره به پایان رسیده است. فردا دوباره تلاش کنید.')
        return False

    code = generate_otp_code()
    try:
        send_otp_sms(phone_number, code)
    except OTPSendError as exc:
        logger.error("Failed to send OTP to %s: %s", phone_number, exc)
        form.add_error(None, 'ارسال پیامک با خطا مواجه شد. لطفاً چند لحظه دیگر دوباره تلاش کنید.')
        return False

    OTPCode.objects.create(phone_number=phone_number, code=code)
    return True


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        return render(request, self.template_name, {'form': RegisterPhoneForm()})

    def post(self, request):
        form = RegisterPhoneForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            if not _issue_otp(request, form, phone_number):
                return render(request, self.template_name, {'form': form})

            request.session['register_data'] = form.cleaned_data
            return redirect('accounts:verify_register')
        return render(request, self.template_name, {'form': form})


class VerifyRegisterView(View):
    template_name = 'accounts/verify.html'

    def get(self, request):
        if 'register_data' not in request.session:
            return redirect('accounts:register')
        return render(request, self.template_name, {'form': VerifyOTPForm()})

    def post(self, request):
        data = request.session.get('register_data')
        if not data:
            return redirect('accounts:register')

        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            phone_number = data['phone_number']

            otp = OTPCode.objects.filter(
                phone_number=phone_number, is_used=False
            ).order_by('-created_at').first()

            if otp and otp.code == code and not otp.is_expired():
                otp.is_used = True
                otp.save(update_fields=['is_used'])

                user = User.objects.create(username=f"user_{uuid.uuid4().hex[:10]}")
                user.set_unusable_password()
                user.save()

                Profile.objects.create(
                    user=user,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=phone_number,
                )

                del request.session['register_data']
                login(request, user, backend='accounts.backends.PhoneOTPBackend')
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد')
                return redirect('website:home')
            else:
                form.add_error('code', 'کد وارد شده اشتباه یا منقضی شده است.')

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, self.template_name, {'form': LoginPhoneForm()})

    def post(self, request):
        form = LoginPhoneForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            if not _issue_otp(request, form, phone_number):
                return render(request, self.template_name, {'form': form})

            request.session['login_phone'] = phone_number
            return redirect('accounts:verify_login')
        return render(request, self.template_name, {'form': form})


class VerifyLoginView(View):
    template_name = 'accounts/verify.html'

    def get(self, request):
        if 'login_phone' not in request.session:
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': VerifyOTPForm()})

    def post(self, request):
        phone_number = request.session.get('login_phone')
        if not phone_number:
            return redirect('accounts:login')

        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            from django.contrib.auth import authenticate
            user = authenticate(request, phone_number=phone_number, code=form.cleaned_data['code'])
            if user is not None:
                del request.session['login_phone']
                login(request, user, backend='accounts.backends.PhoneOTPBackend')
                return redirect('website:home')
            else:
                form.add_error('code', 'کد وارد شده اشتباه یا منقضی شده است.')

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect('website:home')

    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect('website:home')