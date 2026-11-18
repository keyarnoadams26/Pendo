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
    background_color: (0.20, 0.40, 0.94, 1) if self.state == 'normal' else (0.15, 0.33, 0.82, 1)
    color: 1, 1, 1, 1
    bold: True

<SoftButton@Button>:
    background_normal: ''
    background_color: .92, .95, 1, 1
    color: .12, .20, .34, 1

<Card@BoxLayout>:
    orientation: 'vertical'
    padding: dp(14)
    spacing: dp(8)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        Label:
            text: 'pendo'
            font_size: sp(32)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(75)
        Label:
            text: 'Your life, on track.'
            color: .42, .49, .59, 1
            size_hint_y: None
            height: dp(28)
        TextInput:
            id: email
            hint_text: 'Email address'
            multiline: False
            size_hint_y: None
            height: dp(52)
        TextInput:
            id: password
            hint_text: 'Password'
            password: True
            multiline: False
            size_hint_y: None
            height: dp(52)
        PrimaryButton:
            text: 'Sign in'
            size_hint_y: None
            height: dp(50)
            on_release: app.login(email.text, password.text)
        SoftButton:
            text: 'Create an account'
            size_hint_y: None
            height: dp(48)
            on_release: app.signup()
        Label:
            text: 'Demo mode works without Supabase configuration.'
            color: .5, .56, .64, 1
            font_size: sp(11)

<PlanScreen>:
    name: 'plans'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(10)
        Label:
            text: 'Choose your Pendo'
            font_size: sp(23)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(45)
        ScrollView:
            GridLayout:
                cols: 1
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
                Card:
                    Label:
                        text: 'FREE  ·  R0'
                        bold: True
                        color: .08, .14, .25, 1
                    Label:
                        text: 'Tasks, basic calendar, lists, bills and document records.'
                        color: .4, .47, .57, 1
                    PrimaryButton:
                        text: 'Continue free'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Free')
                Card:
                    Label:
                        text: 'PLUS  ·  R29.99 / month'
                        bold: True
                        color: .08, .14, .25, 1
                    Label:
                        text: 'Ad-free, unlimited tasks and lists, advanced calendar and search.'
                        color: .4, .47, .57, 1
                    PrimaryButton:
                        text: 'Select Plus'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Plus')
                Card:
                    Label:
                        text: 'PREMIUM  ·  R59.99 / month'
                        bold: True
                        color: .08, .14, .25, 1
                    Label:
                        text: 'Everything in Plus, with shared tools, summaries and analytics.'
                        color: .4, .47, .57, 1
                    PrimaryButton:
                        text: 'Select Premium'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Premium')

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        Label:
            text: 'pendo'
            font_size: sp(25)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(42)
        Label:
            text: 'Good day, ' + app.username
            font_size: sp(22)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(38)
        Label:
            text: 'Your life, on track.'
            color: .43, .5, .6, 1
            size_hint_y: None
            height: dp(25)
        GridLayout:
            cols: 2
            spacing: dp(8)
            size_hint_y: None
            height: dp(110)
            SoftButton:
                text: 'Tasks & reminders'
                on_release: app.go('tasks')
            SoftButton:
                text: 'Calendar'
                on_release: app.go('calendar')
            SoftButton:
                text: 'Bills & subscriptions'
                on_release: app.go('bills')
            SoftButton:
                text: 'Lists'
                on_release: app.go('lists')
            SoftButton:
                text: 'Documents'
                on_release: app.go('documents')
            SoftButton:
                text: 'Goals & habits'
                on_release: app.go('goals')
        SoftButton:
            text: 'Explore all sections'
            size_hint_y: None
            height: dp(48)
            on_release: app.go('more')
        SoftButton:
            text: 'Settings'
            size_hint_y: None
            height: dp(48)
            on_release: app.go('settings')

<ModuleScreen>:
    name: 'module'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(45)
            Button:
                text: '‹'
                size_hint_x: None
                width: dp(45)
                on_release: app.go('home')
            Label:
                text: app.module_title
                font_size: sp(20)
                bold: True
                color: .07, .12, .22, 1
                halign: 'left'
                text_size: self.size
        TextInput:
            id: module_entry
            hint_text: app.module_hint
            multiline: False
            size_hint_y: None
            height: dp(50)
        PrimaryButton:
            text: 'Add'
            size_hint_y: None
            height: dp(46)
            on_release: app.add_module_item(module_entry.text)
        Label:
            id: sync_status
            text: app.sync_status
            color: .42, .49, .59, 1
            size_hint_y: None
            height: dp(25)
        ScrollView:
            GridLayout:
                id: module_items
                cols: 1
                spacing: dp(8)
                size_hint_y: None
                height: self.minimum_height
        SoftButton:
            text: 'More sections'
            size_hint_y: None
            height: dp(44)
            on_release: app.go('more')

<MoreScreen>:
    name: 'more'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(9)
        Label:
            text: 'Explore Pendo'
            font_size: sp(22)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(45)
        SoftButton:
            text: 'Lists'
            on_release: app.go('lists')
        SoftButton:
            text: 'Documents'
            on_release: app.go('documents')
        SoftButton:
            text: 'Bills & subscriptions'
            on_release: app.go('bills')
        SoftButton:
            text: 'Goals & habits'
            on_release: app.go('goals')
        SoftButton:
            text: 'Upgrade plan'
            on_release: app.go('plans')
        SoftButton:
            text: 'Settings'
            on_release: app.go('settings')
        SoftButton:
            text: 'Owner dashboard (demo)'
            on_release: app.go('admin')
        SoftButton:
            text: 'Home'
            on_release: app.go('home')

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        Label:
            text: 'Settings & account'
            font_size: sp(22)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(45)
        Card:
            Label:
                text: app.username + '\\nPlan: ' + app.plan
                color: .2, .27, .38, 1
        SoftButton:
            text: 'Manage plan'
            on_release: app.go('plans')
        SoftButton:
            text: 'Sign out'
            on_release: app.sign_out()
        SoftButton:
            text: 'Back home'
            on_release: app.go('home')

<AdminScreen>:
    name: 'admin'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        Label:
            text: 'Owner dashboard — demo'
            font_size: sp(22)
            bold: True
            color: .07, .12, .22, 1
            size_hint_y: None
            height: dp(45)
        Label:
            text: 'Analytics and revenue figures are demo data, not live business metrics.'
            color: .65, .35, .1, 1
        SoftButton:
            text: 'Back'
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
            self.plan = saved.get('plan', 'Free')
            self.username = saved.get('username', 'there')
        except (OSError, ValueError, TypeError):
            pass

    def persist_demo(self):
        try:
            with open(self.store_path, 'w', encoding='utf-8') as file:
                json.dump({'plan': self.plan, 'username': self.username}, file)
        except OSError:
            pass

    def login(self, email, password):
        email = email.strip()
        if not email or not password:
            self.notice('Enter an email and password to continue.')
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
        if not self.backend.configured:
            self.notice('Add your Supabase URL and anon key to backend_config.json first.')
            return

        self.notice('Creating account…')
        threading.Thread(
            target=self._auth_worker,
            args=('signup', email, password),
            daemon=True
        ).start()

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
        self.plan = plan
        self.persist_demo()
        if self.backend.configured and self.backend.user:
            threading.Thread(
                target=self._save_plan_worker, args=(plan,), daemon=True
            ).start()
        self.go('home')
        self.notice(plan + ' selected. Payment checkout is not connected yet.')

    def _save_plan_worker(self, plan):
        try:
            self.backend.upsert_profile(display_name=self.username, plan=plan)
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
        if self.backend.configured and self.backend.user:
            if self.cloud_module == self.module_key:
                items.extend(self.cloud_records)
        else:
            items.extend(self.records)

        for item in items:
            row = Button(
                text=str(item),
                size_hint_y=None,
                height=dp(53),
                background_normal='',
                background_color=(1, 1, 1, 1),
                color=(.12, .19, .3, 1),
                halign='left'
            )
            layout.add_widget(row)

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
            self.records.append(value)
            self.refresh_module()
            self.root.get_screen('module').ids.module_entry.text = ''
            self.sync_status = 'Saved on this device in demo mode.'
            self.notice('Added to ' + self.module_title)

    def _load_cloud_records_worker(self, kind):
        try:
            rows = self.backend.list_records(self.RECORD_TYPES[kind])
            values = [
                row.get('content', {}).get('text', str(row.get('content', '')))
                for row in rows
            ]
            Clock.schedule_once(
                lambda _dt: self._apply_cloud_records(kind, values), 0
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
            values = [
                row.get('content', {}).get('text', str(row.get('content', '')))
                for row in rows
            ]
            Clock.schedule_once(
                lambda _dt: self._apply_cloud_records(kind, values), 0
            )
            Clock.schedule_once(
                lambda _dt: self.notice('Saved to your Pendo account.'), 0
            )
        except BackendError as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda _dt: self._cloud_error(kind, message), 0
            )

    def _apply_cloud_records(self, kind, values):
        self.cloud_module = kind
        self.cloud_records = values
        self.sync_status = 'Cloud records synced.'
        if self.module_key == kind and self.root.current == 'module':
            self.refresh_module()

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
