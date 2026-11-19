from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
import json
import os
import threading

from pendo_backend import PendoBackend, BackendError


KV = r"""
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<PrimaryButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    bold: True
    font_size: sp(14)
    size_hint_y: None
    height: dp(50)
    canvas.before:
        Color:
            rgba: (0.12, 0.29, 0.68, 1) if self.state == 'normal' else (0.08, 0.22, 0.55, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<SoftButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: .12, .20, .34, 1
    bold: True
    font_size: sp(13)
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: (.92, .95, .99, 1) if self.state == 'normal' else (.86, .91, .98, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(13)]

<Card@BoxLayout>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(9)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]

<ScreenTitle@Label>:
    color: .07, .12, .22, 1
    font_size: sp(23)
    bold: True
    size_hint_y: None
    height: dp(42)
    halign: 'left'
    text_size: self.size

<HelperText@Label>:
    color: .43, .50, .60, 1
    font_size: sp(12)
    size_hint_y: None
    height: dp(34)
    halign: 'left'
    text_size: self.size

<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(13)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Widget:
            size_hint_y: .7
        Label:
            text: 'pendo'
            font_size: sp(38)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(55)
        Label:
            text: 'A calmer way to organise your life.'
            color: .43, .50, .60, 1
            font_size: sp(14)
            size_hint_y: None
            height: dp(30)
        Card:
            TextInput:
                id: email
                hint_text: 'Email address'
                multiline: False
                size_hint_y: None
                height: dp(50)
                padding: [dp(14), dp(13)]
                background_normal: ''
                background_active: ''
                background_color: (.95, .97, .99, 1)
                foreground_color: (.10, .16, .25, 1)
                cursor_color: (.12, .29, .68, 1)
            TextInput:
                id: password
                hint_text: 'Password'
                password: True
                multiline: False
                size_hint_y: None
                height: dp(50)
                padding: [dp(14), dp(13)]
                background_normal: ''
                background_active: ''
                background_color: (.95, .97, .99, 1)
                foreground_color: (.10, .16, .25, 1)
                cursor_color: (.12, .29, .68, 1)
            PrimaryButton:
                text: 'Sign in'
                on_release: app.login(email.text, password.text)
            SoftButton:
                text: 'Create an account'
                on_release: app.signup()
            SoftButton:
                text: 'Forgot password?'
                on_release: app.reset_password(email.text)
        Label:
            text: 'Securely keep your plans, tasks and essentials together.'
            color: .53, .59, .67, 1
            font_size: sp(11)
            size_hint_y: None
            height: dp(28)
        Widget:
            size_hint_y: .8

<PlanScreen>:
    name: 'plans'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        ScreenTitle:
            text: 'Choose your plan'
        HelperText:
            text: 'Start with the essentials. Upgrade whenever you need more.'
        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
                Card:
                    Label:
                        text: 'FREE'
                        bold: True
                        font_size: sp(12)
                        color: .12, .29, .68, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'R0  /  forever'
                        bold: True
                        font_size: sp(22)
                        color: .07, .12, .22, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'Core tasks, calendar, lists and personal organisation.'
                        color: .43, .50, .60, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(42)
                    PrimaryButton:
                        text: 'Continue with Free'
                        on_release: app.choose_plan('Free')
                Card:
                    Label:
                        text: 'PLUS  ·  MOST POPULAR'
                        bold: True
                        font_size: sp(12)
                        color: .12, .29, .68, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'R29.99  /  month'
                        bold: True
                        font_size: sp(22)
                        color: .07, .12, .22, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'More capacity, advanced calendar tools and search.'
                        color: .43, .50, .60, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(42)
                    PrimaryButton:
                        text: 'Plus · Coming soon'
                        on_release: app.choose_plan('Plus')
                Card:
                    Label:
                        text: 'PREMIUM'
                        bold: True
                        font_size: sp(12)
                        color: .12, .29, .68, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'R59.99  /  month'
                        bold: True
                        font_size: sp(22)
                        color: .07, .12, .22, 1
                        halign: 'left'
                        text_size: self.size
                    Label:
                        text: 'Everything in Plus, with shared tools and insights.'
                        color: .43, .50, .60, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(42)
                    PrimaryButton:
                        text: 'Premium · Coming soon'
                        on_release: app.choose_plan('Premium')
        SoftButton:
            text: 'Back to sign in'
            on_release: app.go('login')

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(11)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(42)
            Label:
                text: 'pendo'
                font_size: sp(25)
                bold: True
                color: .07, .12, .22, 1
                halign: 'left'
                text_size: self.size
            SoftButton:
                text: '⚙'
                size_hint_x: None
                width: dp(48)
                on_release: app.go('settings')
        Label:
            text: 'Good day, ' + app.username
            font_size: sp(23)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(36)
            halign: 'left'
            text_size: self.size
        HelperText:
            text: 'Make space for what matters today.'
        Card:
            Label:
                text: 'YOUR PENDO SPACE'
                font_size: sp(10)
                bold: True
                color: .42, .49, .59, 1
                halign: 'left'
                text_size: self.size
            Label:
                text: 'A little progress adds up.'
                font_size: sp(18)
                bold: True
                color: .07, .12, .22, 1
                halign: 'left'
                text_size: self.size
            Label:
                text: 'Your personal organiser, all in one place.'
                font_size: sp(12)
                color: .43, .50, .60, 1
                halign: 'left'
                text_size: self.size
        Label:
            text: 'YOUR TOOLS'
            font_size: sp(11)
            bold: True
            color: .43, .50, .60, 1
            size_hint_y: None
            height: dp(22)
            halign: 'left'
            text_size: self.size
        GridLayout:
            cols: 2
            spacing: dp(9)
            size_hint_y: None
            height: dp(174)
            SoftButton:
                text: '✓  Tasks'
                on_release: app.go('tasks')
            SoftButton:
                text: '▦  Calendar'
                on_release: app.go('calendar')
            SoftButton:
                text: 'R  Bills'
                on_release: app.go('bills')
            SoftButton:
                text: '☷  Lists'
                on_release: app.go('lists')
            SoftButton:
                text: '▤  Documents'
                on_release: app.go('documents')
            SoftButton:
                text: '◎  Goals & habits'
                on_release: app.go('goals')
        Widget:
            size_hint_y: 1
        SoftButton:
            text: 'Explore all sections'
            on_release: app.go('more')
        Label:
            text: 'PLAN: ' + app.plan.upper()
            color: .50, .57, .66, 1
            font_size: sp(10)
            size_hint_y: None
            height: dp(20)

<ModuleScreen>:
    name: 'module'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            SoftButton:
                text: '‹  Back'
                size_hint_x: None
                width: dp(90)
                on_release: app.go('home')
            Label:
                text: app.module_title
                font_size: sp(19)
                bold: True
                color: .07, .12, .22, 1
                halign: 'left'
                text_size: self.size
        Card:
            Label:
                text: 'ADD NEW'
                color: .43, .50, .60, 1
                font_size: sp(10)
                bold: True
                halign: 'left'
                text_size: self.size
            TextInput:
                id: module_entry
                hint_text: app.module_hint
                multiline: False
                size_hint_y: None
                height: dp(48)
                padding: [dp(12), dp(12)]
                background_normal: ''
                background_active: ''
                background_color: (.95, .97, .99, 1)
                foreground_color: (.10, .16, .25, 1)
                cursor_color: (.12, .29, .68, 1)
                on_text_validate: app.add_module_item(self.text)
            PrimaryButton:
                text: '＋  Add to ' + app.module_title
                on_release: app.add_module_item(module_entry.text)
        Label:
            id: sync_status
            text: app.sync_status
            color: .42, .49, .59, 1
            font_size: sp(11)
            size_hint_y: None
            height: dp(24)
            halign: 'left'
            text_size: self.size
        Label:
            text: 'YOUR ITEMS'
            color: .43, .50, .60, 1
            font_size: sp(10)
            bold: True
            size_hint_y: None
            height: dp(20)
            halign: 'left'
            text_size: self.size
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: module_items
                cols: 1
                spacing: dp(8)
                size_hint_y: None
                height: self.minimum_height
        SoftButton:
            text: 'More sections'
            on_release: app.go('more')

<MoreScreen>:
    name: 'more'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        ScreenTitle:
            text: 'Explore Pendo'
        HelperText:
            text: 'Everything you need, neatly organised.'
        SoftButton:
            text: '✓  Tasks & reminders'
            on_release: app.go('tasks')
        SoftButton:
            text: '▦  Calendar'
            on_release: app.go('calendar')
        SoftButton:
            text: 'R  Bills & subscriptions'
            on_release: app.go('bills')
        SoftButton:
            text: '☷  Lists'
            on_release: app.go('lists')
        SoftButton:
            text: '▤  Documents'
            on_release: app.go('documents')
        SoftButton:
            text: '◎  Goals & habits'
            on_release: app.go('goals')
        SoftButton:
            text: 'Upgrade plan'
            on_release: app.go('plans')
        SoftButton:
            text: 'Settings & account'
            on_release: app.go('settings')
        SoftButton:
            text: 'Owner dashboard (demo)'
            on_release: app.go('admin')
        Widget:
            size_hint_y: 1
        SoftButton:
            text: 'Home'
            on_release: app.go('home')

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        ScreenTitle:
            text: 'Settings & account'
        HelperText:
            text: 'Manage your Pendo account and plan.'
        Card:
            Label:
                text: 'ACCOUNT'
                color: .43, .50, .60, 1
                font_size: sp(10)
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                text: app.username
                color: .07, .12, .22, 1
                font_size: sp(18)
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                text: 'Current plan: ' + app.plan
                color: .43, .50, .60, 1
                halign: 'left'
                text_size: self.size
        SoftButton:
            text: 'Manage subscription / plan'
            on_release: app.go('plans')
        SoftButton:
            text: 'Sign out'
            on_release: app.sign_out()
        Widget:
            size_hint_y: 1
        SoftButton:
            text: 'Back home'
            on_release: app.go('home')

<AdminScreen>:
    name: 'admin'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: (.955, .968, .985, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        ScreenTitle:
            text: 'Owner dashboard'
        Card:
            Label:
                text: 'DEMO PREVIEW'
                color: .70, .40, .12, 1
                bold: True
                font_size: sp(10)
                halign: 'left'
                text_size: self.size
            Label:
                text: 'Analytics and revenue figures are not connected yet.'
                color: .25, .31, .41, 1
                halign: 'left'
                text_size: self.size
        SoftButton:
            text: 'Back to sections'
            on_release: app.go('more')
"""


class LoginScreen(Screen):
    pass


class PlanScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class ModuleScreen(Screen):
    pass


class MoreScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class AdminScreen(Screen):
    pass


class PendoApp(App):
    username = StringProperty('there')
    plan = StringProperty('Free')
    module_title = StringProperty('Tasks')
    module_hint = StringProperty('Add something…')
    sync_status = StringProperty('')
    records = ListProperty([])
    cloud_records = ListProperty([])
    cloud_module = StringProperty('')
    module_key = 'tasks'
    store_path = ''

    RECORD_TYPES = {
        'tasks': 'task',
        'calendar': 'event',
        'bills': 'bill',
        'lists': 'list',
        'documents': 'document',
        'goals': 'goal',
    }

    MODULE_NAMES = {
        'tasks': ('Tasks & reminders', 'Task name or reminder'),
        'calendar': ('Calendar', 'Event title'),
        'bills': ('Bills & subscriptions', 'Bill name and amount, e.g. Internet R400'),
        'lists': ('Lists', 'List title'),
        'documents': ('Documents', 'Document name'),
        'goals': ('Goals & habits', 'Goal name'),
    }

    DEMO_ITEMS = {
        'tasks': ['Finish homework · Today', 'Buy groceries · Today', 'Appointment · Friday'],
        'calendar': ['Today · Personal plans', 'Tomorrow · Study session'],
        'bills': ['Mobile data · R299 · 2 days', 'Streaming · R149 · 5 days'],
        'lists': ['Groceries · 3 items', 'Wish list · 2 items'],
        'documents': ['Warranty · Saved', 'Receipt · Saved'],
        'goals': ['Read 12 books', 'Save for a laptop'],
    }

    def build(self):
        Builder.load_string(KV)
        manager = ScreenManager()
        for screen in (
            LoginScreen(), PlanScreen(), HomeScreen(), ModuleScreen(),
            MoreScreen(), SettingsScreen(), AdminScreen()
        ):
            manager.add_widget(screen)

        self.store_path = os.path.join(self.user_data_dir, 'pendo_demo.json')
        self.backend = PendoBackend(
            os.path.join(os.path.dirname(__file__), 'backend_config.json')
        )
        self.load_demo()
        manager.current = 'login'
        return manager

    def load_demo(self):
        try:
            with open(self.store_path, 'r', encoding='utf-8') as file:
                saved = json.load(file)
            self.plan = 'Free'
            self.username = saved.get('username', 'there')
            stored_records = saved.get('records', {})
            self.records = stored_records if isinstance(stored_records, dict) else {}
        except (OSError, ValueError, TypeError):
            self.records = {}

    def persist_demo(self):
        try:
            with open(self.store_path, 'w', encoding='utf-8') as file:
                json.dump({
                    'plan': 'Free',
                    'username': self.username,
                    'records': dict(self.records)
                }, file)
        except (OSError, TypeError):
            pass

    def login(self, email, password):
        email = email.strip()
        if not email or not password:
            self.notice('Enter an email and password to continue.')
            return
        if '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
            self.notice('Enter a valid email address.')
            return

        if self.backend.configured:
            self.notice('Signing in…')
            threading.Thread(
                target=self._auth_worker,
                args=('signin', email, password),
                daemon=True
            ).start()
            return

        self.username = email.split('@')[0].title() or 'there'
        self.root.current = 'plans'
        self.notice('Demo mode: Supabase is not configured yet.')

    def signup(self):
        screen = self.root.get_screen('login')
        email = screen.ids.email.text.strip()
        password = screen.ids.password.text

        if not email or not password:
            self.notice('Enter an email and password first.')
            return
        if '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
            self.notice('Enter a valid email address.')
            return
        if len(password) < 8:
            self.notice('Use a password with at least 8 characters.')
            return
        if not self.backend.configured:
            self.notice('Add your Supabase URL and anon key to backend_config.json first.')
            return

        self.notice('Creating account…')
        threading.Thread(
            target=self._auth_worker,
            args=('signup', email, password),
            daemon=True
        ).start()

    def reset_password(self, email):
        email = (email or '').strip()
        if not email or '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
            self.notice('Enter your account email address first.')
            return
        if not self.backend.configured:
            self.notice('Password reset needs a configured Supabase connection.')
            return
        self.notice('Requesting a password reset email…')
        threading.Thread(
            target=self._password_reset_worker, args=(email,), daemon=True
        ).start()

    def _password_reset_worker(self, email):
        try:
            self.backend.reset_password(email)
            Clock.schedule_once(
                lambda _dt: self.notice(
                    'If an account exists for that address, Supabase will send password reset instructions. Check your email.'
                ), 0
            )
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(lambda _dt: self.notice(message), 0)

    def _auth_worker(self, action, email, password):
        try:
            if action == 'signin':
                user = self.backend.sign_in(email, password)
                profile = self.backend.get_profile()
                Clock.schedule_once(
                    lambda _dt: self._auth_success(user, profile), 0
                )
            else:
                result = self.backend.sign_up(email, password)
                if not result.get('access_token'):
                    Clock.schedule_once(
                        lambda _dt: self.notice(
                            'Account created. Confirm your email, then sign in.'
                        ), 0
                    )
                else:
                    profile = self.backend.get_profile()
                    Clock.schedule_once(
                        lambda _dt: self._auth_success(result.get('user'), profile), 0
                    )
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(lambda _dt: self.notice(message), 0)

    def _auth_success(self, user, profile):
        email = (user or {}).get('email', '')
        self.username = (
            (profile or {}).get('display_name')
            or (email.split('@')[0].title() if email else 'there')
        )
        self.plan = (profile or {}).get('plan', 'Free')
        self.persist_demo()
        self.root.current = 'home' if profile else 'plans'
        self.notice('Signed in successfully.')

    def choose_plan(self, plan):
        if plan not in ('Free', 'Plus', 'Premium'):
            self.notice('That plan is not available.')
            return
        if plan in ('Plus', 'Premium'):
            self.notice(
                plan + ' checkout is not available yet. Your account will stay on Free until secure payment verification is connected.'
            )
            return

        self.plan = 'Free'
        self.persist_demo()
        if self.backend.configured and self.backend.user:
            threading.Thread(
                target=self._save_profile_name_worker, daemon=True
            ).start()
        self.go('home')
        self.notice('Free plan selected.')

    def _save_profile_name_worker(self):
        try:
            self.backend.upsert_profile(display_name=self.username)
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda _dt: self.notice('Could not save profile: ' + message), 0
            )

    def go(self, screen):
        if screen in self.MODULE_NAMES:
            self.module_key = screen
            self.module_title, self.module_hint = self.MODULE_NAMES[screen]
            self.sync_status = 'Loading cloud records…' if (
                self.backend.configured and self.backend.user
            ) else 'Demo data'
            self.root.current = 'module'
            self.refresh_module()

            if self.backend.configured and self.backend.user:
                threading.Thread(
                    target=self._load_cloud_records_worker,
                    args=(screen,),
                    daemon=True
                ).start()
        else:
            self.root.current = screen

    def refresh_module(self):
        from kivy.uix.button import Button

        layout = self.root.get_screen('module').ids.module_items
        layout.clear_widgets()

        items = list(self.DEMO_ITEMS.get(self.module_key, []))
        local_items = []
        cloud_items = []
        if self.backend.configured and self.backend.user:
            if self.cloud_module == self.module_key:
                cloud_items = list(self.cloud_records)
        else:
            stored = self.records.get(self.module_key, [])
            local_items = stored if isinstance(stored, list) else []
        items.extend(local_items)

        def add_row(label, callback=None):
            row = Button(
                text='   ' + str(label), size_hint_y=None, height=dp(58),
                background_normal='', background_down='',
                background_color=(0, 0, 0, 0), color=(.12, .19, .3, 1),
                halign='left', valign='middle'
            )
            row.text_size = (dp(290), None)
            with row.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(1, 1, 1, 1)
                row._card_bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(14)])
            def update_row_bg(instance, _value):
                instance._card_bg.pos = instance.pos
                instance._card_bg.size = instance.size
            row.bind(pos=update_row_bg, size=update_row_bg)
            if callback:
                row.bind(on_release=lambda *_args: callback())
            layout.add_widget(row)

        for item in items:
            add_row(item)
        for record in cloud_items:
            content = record.get('content') or {}
            label = content.get('text', str(content)) if isinstance(content, dict) else str(content)
            add_row(label + '    ·    Edit / delete', lambda rec=record: self.show_record_actions(rec))

    def add_module_item(self, value):
        value = value.strip()
        if not value:
            self.notice('Type something first.')
            return

        if self.backend.configured and self.backend.user:
            self.sync_status = 'Saving to your account…'
            self.root.get_screen('module').ids.module_entry.text = ''
            threading.Thread(
                target=self._save_record_worker,
                args=(self.module_key, value),
                daemon=True
            ).start()
        else:
            local_items = dict(self.records)
            module_items = list(local_items.get(self.module_key, []))
            module_items.append(value)
            local_items[self.module_key] = module_items
            self.records = local_items
            self.persist_demo()
            self.refresh_module()
            self.root.get_screen('module').ids.module_entry.text = ''
            self.sync_status = 'Saved on this device in demo mode.'
            self.notice('Added to ' + self.module_title)

    def _load_cloud_records_worker(self, kind):
        try:
            rows = self.backend.list_records(self.RECORD_TYPES[kind])
            Clock.schedule_once(
                lambda _dt: self._apply_cloud_records(kind, rows), 0
            )
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda _dt: self._cloud_error(kind, message), 0
            )

    def _save_record_worker(self, kind, value):
        record_type = self.RECORD_TYPES[kind]
        try:
            self.backend.save_record(record_type, {'text': value})
            rows = self.backend.list_records(record_type)
            Clock.schedule_once(
                lambda _dt: self._apply_cloud_records(kind, rows), 0
            )
            Clock.schedule_once(
                lambda _dt: self.notice('Saved to your Pendo account.'), 0
            )
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda _dt: self._cloud_error(kind, message), 0
            )

    def _apply_cloud_records(self, kind, rows):
        self.cloud_module = kind
        self.cloud_records = rows
        self.sync_status = 'Cloud records synced.'
        if self.module_key == kind and self.root.current == 'module':
            self.refresh_module()

    def show_record_actions(self, record):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.metrics import dp

        content = record.get('content') or {}
        current_text = content.get('text', '') if isinstance(content, dict) else str(content)
        panel = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12))
        editor = TextInput(text=str(current_text), multiline=False, size_hint_y=None, height=dp(48))
        panel.add_widget(editor)
        actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save = Button(text='Save changes')
        delete = Button(text='Delete')
        actions.add_widget(save)
        actions.add_widget(delete)
        panel.add_widget(actions)
        popup = Popup(title='Edit record', content=panel, size_hint=(.9, .32))
        save.bind(on_release=lambda *_: (popup.dismiss(), self._update_cloud_record(record.get('id'), editor.text)))
        delete.bind(on_release=lambda *_: (popup.dismiss(), self._delete_cloud_record(record.get('id'))))
        popup.open()

    def _update_cloud_record(self, record_id, value):
        value = (value or '').strip()
        if not value:
            self.notice('A record cannot be empty.')
            return
        kind = self.module_key
        self.sync_status = 'Updating cloud record…'
        threading.Thread(target=self._record_change_worker, args=('update', kind, record_id, value), daemon=True).start()

    def _delete_cloud_record(self, record_id):
        kind = self.module_key
        self.sync_status = 'Deleting cloud record…'
        threading.Thread(target=self._record_change_worker, args=('delete', kind, record_id, ''), daemon=True).start()

    def _record_change_worker(self, action, kind, record_id, value):
        try:
            if action == 'update':
                self.backend.update_record(record_id, {'text': value})
            else:
                self.backend.delete_record(record_id)
            rows = self.backend.list_records(self.RECORD_TYPES[kind])
            Clock.schedule_once(lambda _dt: self._apply_cloud_records(kind, rows), 0)
            message = 'Record updated.' if action == 'update' else 'Record deleted.'
            Clock.schedule_once(lambda _dt: self.notice(message), 0)
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(lambda _dt: self._cloud_error(kind, message), 0)

    def _cloud_error(self, kind, message):
        if self.module_key == kind:
            self.sync_status = 'Cloud sync failed.'
        self.notice('Cloud sync failed: ' + message)

    def sign_out(self):
        if self.backend.configured and self.backend.user:
            try:
                self.backend.sign_out()
            except BackendError:
                pass
        self.cloud_records = []
        self.cloud_module = ''
        self.root.current = 'login'
        self.notice('Signed out.')

    def notice(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label

        Popup(
            title='Pendo',
            content=Label(text=str(message)),
            size_hint=(.84, .3)
        ).open()


if __name__ == '__main__':
    PendoApp().run()
