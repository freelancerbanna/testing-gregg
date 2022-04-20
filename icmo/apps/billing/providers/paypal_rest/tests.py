from decimal import Decimal

from django.test import TestCase
from mock import Mock, patch, call, MagicMock, PropertyMock
import paypalrestsdk

from billing.providers.paypal_rest.handlers import PaypalSubscriptionPlan, PaypalCoupon, \
    PaypalSubscription
from billing.providers.paypal_rest.models import PaypalSubscriptionPlanRegistry, \
    PaypalSubscriptionRegistry, PaypalCouponRegistry

reverse_patcher = patch('billing.providers.paypal_rest.handlers.full_reverse',
                        new=Mock(side_effect=lambda x: x))
reverse_patcher.start()
full_url_patcher = patch('billing.providers.paypal_rest.handlers.full_url_from_path',
                         new=Mock(side_effect=lambda x: x))
full_url_patcher.start()


class PaypalSubscriptionPlanTestCase(TestCase):
    def test_create(self):
        paypal_plan = Mock()
        paypal_plan.id = '5'
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mock_billing_plan_create:
            PaypalSubscriptionPlan.create(
                12, 'Test', 'test', 'statement description', 'short description',
                'month', 3, Decimal('45.25'), 'USD', 'day', 30, Decimal('0.00'), 1,
                'setup fee', Decimal('100.00'), 'setup fee description'
            )
            mock_billing_plan_create.assert_called_once_with(dict(
                name='Test',
                description='short description',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='100.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='3',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.25')
                    ),
                    dict(
                        name='30 Day Trial',
                        type='TRIAL',
                        frequency_interval='30',
                        frequency='day',
                        cycles='1',
                        amount=dict(currency='USD', value='0.00')
                    )
                ]
            ))
        self.assertEqual(
            PaypalSubscriptionPlanRegistry.objects.filter(icmo_plan_id=12).count(),
            1
        )

    def test_update(self):
        with self.assertRaises(NotImplementedError):
            PaypalSubscriptionPlan.update(12)

    def test_change_plan_state(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='5',
            short_description="test",
            currency='USD',
            interval='month',
            interval_count=1,
            amount=Decimal('45.50'),
        )
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='6',
            short_description="test",
            currency='USD',
            interval='month',
            interval_count=1,
            amount=Decimal('45.50'),
        )

        billing_plan = Mock()
        paypalrestsdk.BillingPlan.find = Mock(return_value=billing_plan)

        PaypalSubscriptionPlan.paypal_change_plans_state(12, 'ACTIVE')

        paypalrestsdk.BillingPlan.find.assert_has_calls([
            call('5'),
            call('6')
        ], any_order=True)
        billing_plan.replace.assert_has_calls([
            call([dict(op="replace", path="/", value=dict(state="ACTIVE"))]),
            call([dict(op="replace", path="/", value=dict(state="ACTIVE"))]),
        ])

    def test_activate(self):
        with patch.object(PaypalSubscriptionPlan,
                          'paypal_change_plans_state') as mocked_change_plan_state:
            PaypalSubscriptionPlan.activate(12)

        mocked_change_plan_state.assert_called_once_with(12, 'ACTIVE')

    def test_deactivate(self):
        with patch.object(PaypalSubscriptionPlan,
                          'paypal_change_plans_state') as mocked_change_plan_state:
            PaypalSubscriptionPlan.deactivate(12)

        mocked_change_plan_state.assert_called_once_with(12, 'INACTIVE')

    def test_delete(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='5',
            short_description="test",
            currency='USD',
            interval='month',
            interval_count=1,
            amount=Decimal('45.50'),
        )
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='6',
            short_description="test",
            currency='USD',
            interval='month',
            interval_count=1,
            amount=Decimal('45.50'),
        )
        with patch.object(PaypalSubscriptionPlan,
                          '_paypal_change_paypal_plan_state') as mocked_change_plan_state:
            PaypalSubscriptionPlan.delete(12)

        mocked_change_plan_state.assert_has_calls([call('5', 'DELETED'), call('6', 'DELETED')], any_order=True)

        self.assertEqual(
            PaypalSubscriptionPlanRegistry.objects.filter(icmo_plan_id=12).count(), 0
        )


class PaypalSubscriptionExistingCouponsTestCase(TestCase):
    def setUp(self):
        self.paypal_coupon = PaypalCouponRegistry.objects.create(
            icmo_coupon_id=1,
            short_description='Test coupon',
            code='test',
            duration='forever',
            percent_off=50
        )

    def test_create(self):
        paypal_plan = Mock()
        type(paypal_plan).id = PropertyMock(side_effect=['3000', '3001'])
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mock_billing_plan_create:
            PaypalSubscriptionPlan.create(
                12, 'Test', 'test', 'statement description', 'short description',
                'month', 3, Decimal('45.25'), 'USD', 'day', 30, Decimal('0.00'), 1,
                'setup fee', Decimal('100.00'), 'setup fee description'
            )
        mock_billing_plan_create.assert_has_calls([
            call(dict(
                name='Test',
                description='short description',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='100.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='3',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.25')
                    ),
                    dict(
                        name='30 Day Trial',
                        type='TRIAL',
                        frequency_interval='30',
                        frequency='day',
                        cycles='1',
                        amount=dict(currency='USD', value='0.00')
                    )
                ]
            )),
            call(dict(
                name='Test',
                description='short description test discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='100.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='3',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='22.62')
                    ),
                    dict(
                        name='30 Day Trial',
                        type='TRIAL',
                        frequency_interval='30',
                        frequency='day',
                        cycles='1',
                        amount=dict(currency='USD', value='0.00')
                    )
                ]
            ))
        ])
        self.assertEqual(
            PaypalSubscriptionPlanRegistry.objects.filter(icmo_plan_id=12).count(),
            2
        )


class PaypalSubscriptionTestCase(TestCase):
    def setUp(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='paypal_plan_id_1',
            name='Example Subscription Plan 1',
            short_description='plan description',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('100.00')
        )
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            icmo_coupon_id=55,
            paypal_plan_id='paypal_plan_id_2',
            name='Example Subscription Plan 1',
            short_description='plan description discounted',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('100.00')
        )
        PaypalSubscriptionRegistry.objects.create(
            icmo_subscription_id=3100,
            paypal_plan_id='paypal_plan_id_2',
            paypal_subscription_id='delete_test_id'
        )
        self.date_patcher = patch('billing.providers.paypal_rest.handlers.get_utc_timestamp',
                                  new=MagicMock(return_value='timestamp'))
        self.date_patcher.start()

    def tearDown(self):
        self.date_patcher.stop()

    def test_paypal_create_subscription_agreement(self):
        mocked_agreement = MagicMock()
        mocked_agreement.__getitem__.return_value = [
            dict(rel='approval_url', href='http://www.approve.com/')]
        with patch.object(paypalrestsdk, 'BillingAgreement',
                          return_value=mocked_agreement) as mocked_billing_agreement:
            url = PaypalSubscription.paypal_create_subscription_agreement(
                12, 'Example Subscription Plan 1', '/cancel/', None
            )
        mocked_billing_agreement.assert_called_once_with(dict(
            name="Example Subscription Plan 1 Agreement",
            description="Example Subscription Plan 1 Agreement",
            start_date='timestamp',
            plan=dict(
                id='paypal_plan_id_1'
            ),
            payer=dict(
                payment_method='paypal'
            ),
            override_merchant_preferences=dict(
                cancel_url='/cancel/',
                return_url='billing:paypal:paypal_authorized'
            )
        ))

        self.assertEqual(url, 'http://www.approve.com/')

    def test_paypal_create_subscription_agreement_coupon(self):
        mocked_agreement = MagicMock()
        mocked_agreement.__getitem__.return_value = [
            dict(rel='approval_url', href='http://www.approve.com/')]
        with patch.object(paypalrestsdk, 'BillingAgreement',
                          return_value=mocked_agreement) as mocked_billing_agreement:
            url = PaypalSubscription.paypal_create_subscription_agreement(
                12, 'Example Subscription Plan 1', '/cancel/', 55
            )
        mocked_billing_agreement.assert_called_once_with(dict(
            name="Example Subscription Plan 1 Agreement",
            description="Example Subscription Plan 1 Agreement",
            start_date='timestamp',
            plan=dict(
                id='paypal_plan_id_2'
            ),
            payer=dict(
                payment_method='paypal'
            ),
            override_merchant_preferences=dict(
                cancel_url='/cancel/',
                return_url='billing:paypal:paypal_authorized'
            )
        ))

        self.assertEqual(url, 'http://www.approve.com/')

    def test_create(self):
        with patch.object(PaypalSubscription,
                          'paypal_execute_subscription',
                          return_value='3000') as mocked_paypal_execute:
            PaypalSubscription.create(
                99, 12, 'cordery@gmail.com', 'Andrew Cordery', 'paymenttoken', 55
            )
        mocked_paypal_execute.assert_called_once_with('paymenttoken')
        self.assertEqual(
            PaypalSubscriptionRegistry.objects.filter(icmo_subscription_id=99).count(),
            1
        )
        sub_link = PaypalSubscriptionRegistry.objects.get(icmo_subscription_id=99)
        self.assertEqual(sub_link.paypal_plan_id, 'paypal_plan_id_2')
        self.assertEqual(sub_link.paypal_subscription_id, '3000')

    def test_paypal_execute_subscription(self):
        billing_agreement = Mock()
        billing_agreement.id = '3100'

        with patch.object(paypalrestsdk.BillingAgreement, 'execute',
                          return_value=billing_agreement) as mocked_execute:
            id = PaypalSubscription.paypal_execute_subscription('payment_token')
        mocked_execute.assert_called_once_with('payment_token')
        self.assertEqual(id, '3100')

    def test_cancel(self):
        billing_agreement = Mock()

        with patch.object(paypalrestsdk.BillingAgreement, 'find',
                          return_value=billing_agreement) as mocked_find:
            PaypalSubscription.cancel(12, at_period_end=False, note='note')

        mocked_find.assert_called_once_with(12)

        billing_agreement.cancel.assert_called_once_with(dict(note='note'))

        self.assertEqual(
            PaypalSubscriptionRegistry.objects.filter(paypal_plan_id='delete_test_id').count(),
            0
        )


class PaypalCouponExistingPlanTestCase(TestCase):
    def setUp(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='paypal_plan_id_1',
            name='Example Subscription Plan 1',
            short_description='plan description',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('0')
        )
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=14,
            paypal_plan_id='paypal_plan_id_2',
            name='Example Subscription Plan 2',
            short_description='plan description',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('0')
        )

    def test_create(self):
        paypal_plan = Mock()
        type(paypal_plan).id = PropertyMock(side_effect=['3000', '3001'])
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mocked_billing_plan:
            PaypalCoupon.create(
                22, 'testcode', 'short description', 'repeating', Decimal('25'), None,
                'USD', 12, None, None, None, None
            )
        mocked_billing_plan.assert_has_calls([
            call(dict(
                name='Example Subscription Plan 1',
                description='plan description testcode discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='0.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='1',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.50')
                    ),
                    dict(
                        name='12 Month Discounted Rate',
                        type='TRIAL',
                        frequency_interval='1',
                        frequency='month',
                        cycles='12',
                        amount=dict(currency='USD', value='20.50')
                    )
                ]
            )),
            call(dict(
                name='Example Subscription Plan 2',
                description='plan description testcode discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='0.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='1',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.50')
                    ),
                    dict(
                        name='12 Month Discounted Rate',
                        type='TRIAL',
                        frequency_interval='1',
                        frequency='month',
                        cycles='12',
                        amount=dict(currency='USD', value='20.50')
                    )
                ]
            ))
        ], any_order=True)


class PaypalCouponDiscountTestCase(TestCase):
    def setUp(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            paypal_plan_id='notused',
            name='Example Subscription Plan 1',
            short_description='plan description',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('100.00')
        )

    def test_create_repeating(self):
        paypal_plan = Mock()
        paypal_plan.id = "3000"
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mocked_billing_plan:
            PaypalCoupon.create(
                22, 'testcode', 'short description', 'repeating', Decimal('25.00'), None,
                'USD', 12, None, None, None, None
            )
        mocked_billing_plan.assert_called_once_with(
            dict(
                name='Example Subscription Plan 1',
                description='plan description testcode discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='100.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='1',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.50')
                    ),
                    dict(
                        name='12 Month Discounted Rate',
                        type='TRIAL',
                        frequency_interval='1',
                        frequency='month',
                        cycles='12',
                        amount=dict(currency='USD', value='20.50')
                    )
                ]
            )
        )

    def test_create_forever(self):
        paypal_plan = Mock()
        paypal_plan.id = "3000"
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mocked_billing_plan:
            PaypalCoupon.create(
                22, 'testcode', 'short description', 'forever', None, 25,
                'USD', 12, None, None, None, None
            )
        mocked_billing_plan.assert_called_once_with(
            dict(
                name='Example Subscription Plan 1',
                description='plan description testcode discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='100.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='1',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='34.12')
                    )
                ]
            )
        )

    def test_create_setup_discount(self):
        paypal_plan = Mock()
        paypal_plan.id = "3000"
        with patch.object(paypalrestsdk, 'BillingPlan',
                          return_value=paypal_plan) as mocked_billing_plan:
            PaypalCoupon.create(
                22, 'testcode', 'short description', 'repeating', None, 25,
                'USD', 12, None, None, None, 25
            )
        mocked_billing_plan.assert_called_once_with(
            dict(
                name='Example Subscription Plan 1',
                description='plan description testcode discount applied',
                type='INFINITE',
                merchant_preferences=dict(
                    auto_bill_amount='YES',
                    cancel_url='billing:paypal:paypal_canceled',
                    return_url='billing:paypal:paypal_authorized',
                    max_fail_attempts='3',
                    initial_fail_amount_action='CANCEL',
                    setup_fee=dict(currency='USD', value='75.00')
                ),
                payment_definitions=[
                    dict(
                        name='Month',
                        type='REGULAR',
                        frequency_interval='1',
                        frequency='month',
                        cycles='0',
                        amount=dict(currency='USD', value='45.50')
                    ),
                    dict(
                        name='12 Month Discounted Rate',
                        type='TRIAL',
                        frequency_interval='1',
                        frequency='month',
                        cycles='12',
                        amount=dict(currency='USD', value='34.12')
                    )
                ]
            )
        )


class PaypalCouponTestCase(TestCase):
    def setUp(self):
        PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            icmo_coupon_id=55,
            paypal_plan_id='notused',
            name='Example Subscription Plan 1',
            short_description='plan description',
            currency='USD',
            interval='month',
            interval_count='1',
            amount=Decimal('45.50'),
            setup_fee_amount=Decimal('100.00')
        )

    def test_update(self):
        with self.assertRaises(NotImplementedError):
            PaypalCoupon.update(55)

    def test_deactivate(self):
        self.assertTrue(PaypalCoupon.deactivate(55))

    def test_activate(self):
        self.assertTrue(PaypalCoupon.activate(55))

    def test_delete(self):
        self.assertTrue(PaypalCoupon.delete(55))

        self.assertEqual(
            PaypalSubscriptionPlanRegistry.objects.filter(icmo_coupon_id=55).count(),
            0
        )
