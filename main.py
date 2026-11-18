from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import date, timedelta
import json, os, threading
from pendo_backend import PendoBackend, BackendError

KV = r"""
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
<PrimaryButton@Button>:
    background_normal: ''
    background_color: 0,0,0,0
    color: 1,1,1
    bold: True
    canvas.before:
        Color:
            rgba: (0.20,0.40,0.94,1) if self.state == 'normal' else (0.15,0.33,0.82,1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(13)]
<SoftButton@Button>:
    background_normal: ''
    background_color: 0,0,0,0
    color: 0.15,0.23,0.38,1
    canvas.before:
        Color:
            rgba: 0.92,0.95,1,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
<Card@BoxLayout>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(8)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: 1,1,1,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        Widget:
            size_hint_y: .12
        BoxLayout:
            size_hint_y: None
            height: dp(65)
            spacing: dp(12)
            Label:
                text: 'p'
                font_size: sp(42)
                bold: True
                color: 0.07,0.12,0.22,1
                size_hint_x: None
                width: dp(54)
                canvas.before:
                    Color:
                        rgba: 1,1,1,1
                    RoundedRectangle:
                        pos: self.x, self.y+dp(4)
                        size: self.width, self.height-dp(8)
                        radius: [dp(15)]
            BoxLayout:
                orientation: 'vertical'
                Label:
                    text: 'pendo'
                    font_size: sp(26)
                    bold: True
                    color: 0.07,0.12,0.22,1
                    halign: 'left'
                    text_size: self.size
                Label:
                    text: 'Your life, on track.'
                    font_size: sp(13)
                    color: 0.45,0.51,0.60,1
                    halign: 'left'
                    text_size: self.size
        Widget:
            size_hint_y: .05
        Label:
            text: 'Welcome back'
            font_size: sp(27)
            bold: True
            color: 0.08,0.13,0.23,1
            size_hint_y: None
            height: dp(38)
            halign: 'left'
            text_size: self.size
        Label:
            text: 'Sign in to keep everything in one place.'
            font_size: sp(14)
            color: 0.45,0.51,0.60,1
            size_hint_y: None
            height: dp(26)
            halign: 'left'
            text_size: self.size
        TextInput:
            id: email
            hint_text: 'Email address'
            multiline: False
            size_hint_y: None
            height: dp(52)
            padding: [dp(14),dp(15)]
            background_normal: ''
            background_active: ''
            background_color: 1,1,1,1
            foreground_color: 0.1,0.15,0.25,1
        TextInput:
            id: password
            hint_text: 'Password'
            password: True
            multiline: False
            size_hint_y: None
            height: dp(52)
            padding: [dp(14),dp(15)]
            background_normal: ''
            background_active: ''
            background_color: 1,1,1,1
            foreground_color: 0.1,0.15,0.25,1
        Label:
            text: 'Forgot password?'
            size_hint_y: None
            height: dp(28)
            color: 0.20,0.40,0.94,1
            halign: 'right'
            text_size: self.size
        PrimaryButton:
            text: 'Sign in'
            size_hint_y: None
            height: dp(52)
            on_release: app.login(email.text, password.text)
        SoftButton:
            text: 'Create an account'
            size_hint_y: None
            height: dp(50)
            on_release: app.signup()
        Label:
            text: 'Demo mode: any email and password will continue.'
            font_size: sp(11)
            color: 0.55,0.60,0.68,1
            size_hint_y: None
            height: dp(25)
        Widget:
            size_hint_y: .2

<PlanScreen>:
    name: 'plans'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(17)
        spacing: dp(9)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(35)
            Label:
                text: 'Choose your Pendo'
                bold: True
                font_size: sp(22)
                color: 0.07,0.12,0.22,1
                halign: 'left'
                text_size: self.size
        Label:
            text: 'Start free. Upgrade when you need more.'
            size_hint_y: None
            height: dp(25)
            font_size: sp(13)
            color: 0.45,0.51,0.60,1
            halign: 'left'
            text_size: self.size
        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                spacing: dp(11)
                size_hint_y: None
                height: self.minimum_height
                Card:
                    Label:
                        text: 'FREE'
                        bold: True
                        color: 0.16,0.23,0.36,1
                        font_size: sp(14)
                        size_hint_y: None
                        height: dp(25)
                    Label:
                        text: 'R0  ·  Forever'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(23)
                        size_hint_y: None
                        height: dp(33)
                    Label:
                        text: 'Reminders & tasks  •  Basic calendar\\n5 lists  •  Basic bills  •  10 document records\\nAds included'
                        color: 0.40,0.47,0.58,1
                        font_size: sp(12)
                        size_hint_y: None
                        height: dp(63)
                    PrimaryButton:
                        text: 'Continue free'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Free')
                Card:
                    Label:
                        text: 'PLUS  ·  POPULAR'
                        bold: True
                        color: 0.20,0.40,0.94,1
                        font_size: sp(14)
                        size_hint_y: None
                        height: dp(25)
                    Label:
                        text: 'R29.99 / month'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(23)
                        size_hint_y: None
                        height: dp(33)
                    Label:
                        text: 'R249 / year  •  Save R110.88\\nAd-free  •  Unlimited tasks & lists\\nBills & subscriptions  •  100 documents\\nAdvanced calendar, search & themes'
                        color: 0.40,0.47,0.58,1
                        font_size: sp(12)
                        size_hint_y: None
                        height: dp(80)
                    PrimaryButton:
                        text: 'Select Plus'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Plus')
                Card:
                    Label:
                        text: 'PREMIUM'
                        bold: True
                        color: 0.16,0.23,0.36,1
                        font_size: sp(14)
                        size_hint_y: None
                        height: dp(25)
                    Label:
                        text: 'R59.99 / month'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(23)
                        size_hint_y: None
                        height: dp(33)
                    Label:
                        text: 'R499 / year  •  Save R220.88\\nEverything in Plus  •  AI assistant\\nShared & household tools  •  Smart summaries\\nAnalytics  •  Priority support'
                        color: 0.40,0.47,0.58,1
                        font_size: sp(12)
                        size_hint_y: None
                        height: dp(80)
                    PrimaryButton:
                        text: 'Select Premium'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.choose_plan('Premium')

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                spacing: dp(12)
                padding: dp(15),dp(15),dp(15),dp(10)
                size_hint_y: None
                height: self.minimum_height
                BoxLayout:
                    size_hint_y: None
                    height: dp(54)
                    Label:
                        text: 'pendo'
                        bold: True
                        font_size: sp(23)
                        color: 0.07,0.12,0.22,1
                        halign: 'left'
                        text_size: self.size
                    SoftButton:
                        text: '⚙'
                        size_hint_x: None
                        width: dp(48)
                        on_release: app.go('settings')
                Label:
                    text: 'Good day, ' + app.username + ' 👋'
                    font_size: sp(22)
                    bold: True
                    color: 0.07,0.12,0.22,1
                    size_hint_y: None
                    height: dp(32)
                    halign: 'left'
                    text_size: self.size
                Label:
                    text: 'Here’s what’s on your plate today.'
                    color: 0.45,0.51,0.60,1
                    size_hint_y: None
                    height: dp(24)
                    halign: 'left'
                    text_size: self.size
                GridLayout:
                    cols: 2
                    spacing: dp(9)
                    size_hint_y: None
                    height: dp(165)
                    Card:
                        Label:
                            text: 'DUE TODAY'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                        Label:
                            text: str(app.today_count)
                            bold: True
                            color: 0.07,0.12,0.22,1
                            font_size: sp(27)
                        Label:
                            text: 'Things to do'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                    Card:
                        Label:
                            text: 'UPCOMING'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                        Label:
                            text: str(app.upcoming_count)
                            bold: True
                            color: 0.07,0.12,0.22,1
                            font_size: sp(27)
                        Label:
                            text: 'Next 7 days'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                    Card:
                        Label:
                            text: 'BILLS TRACKED'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                        Label:
                            text: 'R' + str(app.bill_total)
                            bold: True
                            color: 0.07,0.12,0.22,1
                            font_size: sp(22)
                        Label:
                            text: 'Unpaid'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                    Card:
                        Label:
                            text: 'COMPLETED'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                        Label:
                            text: str(app.completed_count)
                            bold: True
                            color: 0.07,0.12,0.22,1
                            font_size: sp(27)
                        Label:
                            text: 'This week'
                            color: 0.45,0.51,0.60,1
                            font_size: sp(11)
                Card:
                    Label:
                        text: 'Today’s focus'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(16)
                        size_hint_y: None
                        height: dp(28)
                    Label:
                        text: app.today_summary
                        color: 0.38,0.46,0.57,1
                        font_size: sp(13)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    PrimaryButton:
                        text: 'Open tasks'
                        size_hint_y: None
                        height: dp(45)
                        on_release: app.go('tasks')
                Card:
                    Label:
                        text: 'Quick add'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(16)
                        size_hint_y: None
                        height: dp(28)
                    GridLayout:
                        cols: 2
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(100)
                        SoftButton:
                            text: '+ Task / reminder'
                            on_release: app.go('tasks')
                        SoftButton:
                            text: '+ Bill'
                            on_release: app.go('bills')
                        SoftButton:
                            text: '+ List'
                            on_release: app.go('lists')
                        SoftButton:
                            text: '+ Document'
                            on_release: app.go('documents')
                Card:
                    Label:
                        text: 'Payments coming up'
                        bold: True
                        color: 0.07,0.12,0.22,1
                        font_size: sp(16)
                        size_hint_y: None
                        height: dp(28)
                    Label:
                        text: app.bill_summary
                        color: 0.38,0.46,0.57,1
                        font_size: sp(13)
                        halign: 'left'
                        text_size: self.size
                    SoftButton:
                        text: 'View bills'
                        size_hint_y: None
                        height: dp(43)
                        on_release: app.go('bills')
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(5)
            spacing: dp(3)
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: '⌂\\nHome'
                background_color: 0,0,0,0
                color: 0.20,0.40,0.94,1
                on_release: app.go('home')
            Button:
                text: '✓\\nTasks'
                background_color: 0,0,0,0
                color: 0.40,0.47,0.58,1
                on_release: app.go('tasks')
            Button:
                text: '▦\\nCalendar'
                background_color: 0,0,0,0
                color: 0.40,0.47,0.58,1
                on_release: app.go('calendar')
            Button:
                text: '◈\\nBills'
                background_color: 0,0,0,0
                color: 0.40,0.47,0.58,1
                on_release: app.go('bills')
            Button:
                text: '☷\\nMore'
                background_color: 0,0,0,0
                color: 0.40,0.47,0.58,1
                on_release: app.go('more')

<ModuleScreen>:
    name: 'module'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '‹'
                font_size: sp(26)
                size_hint_x: None
                width: dp(45)
                background_color: 0,0,0,0
                color: 0.15,0.23,0.38,1
                on_release: app.go('home')
            Label:
                text: app.module_title
                bold: True
                font_size: sp(20)
                color: 0.07,0.12,0.22,1
                halign: 'left'
                text_size: self.size
        TextInput:
            id: module_entry
            hint_text: app.module_hint
            multiline: False
            size_hint_y: None
            height: dp(50)
            padding: dp(13)
            background_normal: ''
            background_color: 1,1,1,1
        PrimaryButton:
            text: 'Add'
            size_hint_y: None
            height: dp(46)
            on_release: app.add_module_item(module_entry.text)
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: module_items
                cols: 1
                spacing: dp(9)
                size_hint_y: None
                height: self.minimum_height
        SoftButton:
            text: 'Switch section'
            size_hint_y: None
            height: dp(46)
            on_release: app.go('more')

<MoreScreen>:
    name: 'more'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Explore Pendo'
            font_size: sp(22)
            bold: True
            color: 0.07,0.12,0.22,1
            size_hint_y: None
            height: dp(42)
            halign: 'left'
            text_size: self.size
        ScrollView:
            GridLayout:
                cols: 1
                spacing: dp(9)
                size_hint_y: None
                height: self.minimum_height
                SoftButton:
                    text: '☷   Lists'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('lists')
                SoftButton:
                    text: '▤   Documents'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('documents')
                SoftButton:
                    text: '◈   Bills & subscriptions'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('bills')
                SoftButton:
                    text: '◎   Goals & habits'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('goals')
                SoftButton:
                    text: '✦   Upgrade plan'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('plans')
                SoftButton:
                    text: '⚙   Settings'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('settings')
                SoftButton:
                    text: '▣   Owner dashboard (demo)'
                    size_hint_y: None
                    height: dp(52)
                    on_release: app.go('admin')
        SoftButton:
            text: 'Home'
            size_hint_y: None
            height: dp(46)
            on_release: app.go('home')

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Settings & account'
            font_size: sp(21)
            bold: True
            color: 0.07,0.12,0.22,1
            size_hint_y: None
            height: dp(42)
            halign: 'left'
            text_size: self.size
        Card:
            Label:
                text: 'Account'
                bold: True
                color: 0.07,0.12,0.22,1
            Label:
                text: app.username + '\\nPlan: ' + app.plan
                color: 0.4,0.47,0.58,1
        SoftButton:
            text: 'Manage plan'
            size_hint_y: None
            height: dp(48)
            on_release: app.go('plans')
        SoftButton:
            text: 'Notification preferences (demo)'
            size_hint_y: None
            height: dp(48)
            on_release: app.notice('Notification settings are planned for the backend-connected build.')
        SoftButton:
            text: 'Sign out'
            size_hint_y: None
            height: dp(48)
            on_release: app.go('login')
        SoftButton:
            text: 'Back home'
            size_hint_y: None
            height: dp(48)
            on_release: app.go('home')

<AdminScreen>:
    name: 'admin'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.96,0.97,0.99,1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Owner dashboard'
            font_size: sp(22)
            bold: True
            color: 0.07,0.12,0.22,1
            size_hint_y: None
            height: dp(42)
            halign: 'left'
            text_size: self.size
        Label:
            text: 'DEMO ANALYTICS — not connected to live users or revenue'
            color: 0.72,0.39,0.10,1
            font_size: sp(11)
            size_hint_y: None
            height: dp(28)
        GridLayout:
            cols: 2
            spacing: dp(8)
            size_hint_y: None
            height: dp(170)
            Card:
                Label:
                    text: 'Users'
                    color: 0.45,0.51,0.60,1
                Label:
                    text: '128'
                    font_size: sp(26)
                    bold: True
                    color: 0.07,0.12,0.22,1
                Label:
                    text: '+18 this month'
                    color: 0.15,0.55,0.39,1
            Card:
                Label:
                    text: 'MRR'
                    color: 0.45,0.51,0.60,1
                Label:
                    text: 'R2,149'
                    font_size: sp(26)
                    bold: True
                    color: 0.07,0.12,0.22,1
                Label:
                    text: 'Demo amount'
                    color: 0.45,0.51,0.60,1
            Card:
                Label:
                    text: 'Active users'
                    color: 0.45,0.51,0.60,1
                Label:
                    text: '76'
                    font_size: sp(26)
                    bold: True
                    color: 0.07,0.12,0.22,1
                Label:
                    text: 'Demo'
                    color: 0.45,0.51,0.60,1
            Card:
                Label:
                    text: 'Premium'
                    color: 0.45,0.51,0.60,1
                Label:
                    text: '23'
                    font_size: sp(26)
                    bold: True
                    color: 0.07,0.12,0.22,1
                Label:
                    text: 'Demo subscribers'
                    color: 0.45,0.51,0.60,1
        Card:
            Label:
                text: 'Admin tools'
                bold: True
                color: 0.07,0.12,0.22,1
            Label:
                text: 'User management • Subscription management\\nSales & revenue reports • App analytics\\nFeedback & support • Announcements\\nFeature controls • Ad management'
                color: 0.4,0.47,0.58,1
                font_size: sp(12)
        SoftButton:
            text: 'Back'
            size_hint_y: None
            height: dp(46)
            on_release: app.go('more')
"""
class LoginScreen(Screen): pass
class PlanScreen(Screen): pass
class HomeScreen(Screen): pass
class ModuleScreen(Screen): pass
class MoreScreen(Screen): pass
class SettingsScreen(Screen): pass
class AdminScreen(Screen): pass

class PendoApp(App):
    username=StringProperty('there')
    plan=StringProperty('Free')
    module_title=StringProperty('Tasks')
    module_hint=StringProperty('Add something…')
    today_count=StringProperty('3')
    upcoming_count=StringProperty('8')
    completed_count=StringProperty('12')
    bill_total=StringProperty('1,240')
    today_summary=StringProperty('Finish assignment\\nBuy groceries\\nReply to email')
    bill_summary=StringProperty('Mobile data · R299\\nStreaming · R149\\nInternet · R393')
    records=ListProperty([])
    module_key='tasks'
    store_path=''
    def build(self):
        Builder.load_string(KV)
        sm=ScreenManager()
        for s in (LoginScreen(),PlanScreen(),HomeScreen(),ModuleScreen(),MoreScreen(),SettingsScreen(),AdminScreen()):
            sm.add_widget(s)
        self.store_path=os.path.join(self.user_data_dir,'pendo_demo.json')
        self.backend=PendoBackend(os.path.join(os.path.dirname(__file__),'backend_config.json'))
        self.load_demo()
        sm.current='login'
        return sm
    def load_demo(self):
        try:
            with open(self.store_path) as f:
                saved=json.load(f)
                self.plan=saved.get('plan','Free')
                self.username=saved.get('username','there')
        except Exception: pass
    def persist_demo(self):
        try:
            with open(self.store_path,'w') as f: json.dump({'plan':self.plan,'username':self.username},f)
        except Exception: pass
    def login(self,email,password):
        if not email.strip() or not password:
            self.notice('Enter an email and password to continue.')
            return
        if self.backend.configured:
            self.notice('Signing in…')
            threading.Thread(target=self._auth_worker,args=('signin',email.strip(),password),daemon=True).start()
            return
        self.username=email.split('@')[0].title() or 'there'
        self.root.current='plans'
        self.notice('Demo mode: backend not configured yet.')
    def signup(self):
        sc=self.root.get_screen('login')
        email=sc.ids.email.text.strip()
        password=sc.ids.password.text
        if not email or not password:
            self.notice('Enter an email and password, then tap Create an account.')
            return
        if not self.backend.configured:
            self.notice('Backend setup required. Add your Supabase URL and anon key in backend_config.json.')
            return
        self.notice('Creating account…')
        threading.Thread(target=self._auth_worker,args=('signup',email,password),daemon=True).start()
    def _auth_worker(self,action,email,password):
        try:
            if action=='signin':
                user=self.backend.sign_in(email,password)
                profile=self.backend.get_profile()
                Clock.schedule_once(lambda _dt:self._auth_success(user,profile),0)
            else:
                result=self.backend.sign_up(email,password)
                if not result.get('access_token'):
                    Clock.schedule_once(lambda _dt:self.notice('Account created. Check your email to confirm, then sign in.'),0)
                else:
                    profile=self.backend.get_profile()
                    Clock.schedule_once(lambda _dt:self._auth_success(result.get('user'),profile),0)
        except BackendError as exc:
            msg=str(exc)
            Clock.schedule_once(lambda _dt:self.notice(msg),0)
    def _auth_success(self,user,profile):
        email=(user or {}).get('email','')
        self.username=(profile or {}).get('display_name') or (email.split('@')[0].title() if email else 'there')
        self.plan=(profile or {}).get('plan','Free')
        self.root.current='home' if profile else 'plans'
        self.notice('Signed in successfully.')
    def choose_plan(self,p):
        self.plan=p
        self.persist_demo()
        if self.backend.configured and self.backend.user:
            threading.Thread(target=self._save_plan_worker,args=(p,),daemon=True).start()
        self.go('home')
        self.notice(p+' selected. Checkout is not connected yet.')
    def _save_plan_worker(self,p):
        try:
            self.backend.upsert_profile(display_name=self.username)
        except BackendError as exc:
            msg=str(exc)
            Clock.schedule_once(lambda _dt:self.notice('Could not save plan: '+msg),0)
    def go(self,screen):
        if screen in ('tasks','calendar','bills','lists','documents','goals'):
            self.module_key=screen
            names={'tasks':'Tasks & reminders','calendar':'Calendar','bills':'Bills & subscriptions','lists':'Lists','documents':'Documents','goals':'Goals & habits'}
            hints={'tasks':'Task name — tap Add','calendar':'Event title — tap Add','bills':'Bill name and amount, e.g. Internet R400','lists':'List title','documents':'Document name','goals':'Goal name'}
            self.module_title=names[screen]
            self.module_hint=hints[screen]
            self.root.current='module'
            self.refresh_module()
        else:self.root.current=screen
    def refresh_module(self):
        sc=self.root.get_screen('module')
        layout=sc.ids.module_items
        layout.clear_widgets()
        samples={'tasks':['Finish homework · Today','Buy groceries · Today','Appointment · Friday'],'calendar':['Today · Personal plans','Tomorrow · Study session'],'bills':['Mobile data · R299 · 2 days','Streaming · R149 · 5 days'],'lists':['Groceries · 3 items','Wish list · 2 items'],'documents':['Warranty · Saved','Receipt · Saved'],'goals':['Read 12 books','Save for a laptop']}
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        for x in samples.get(self.module_key,[])+self.records:
            row=Button(text=x,size_hint_y=None,height=dp(53),background_normal='',background_color=(1,1,1,1),color=(.12,.19,.3,1),halign='left')
            layout.add_widget(row)
    def add_module_item(self,value):
        if not value.strip():
            self.notice('Type something first.')
            return
        self.records.append(value.strip())
        if self.backend.configured and self.backend.user:
            threading.Thread(target=self._save_record_worker,args=(self.module_key,value.strip()),daemon=True).start()
        self.refresh_module()
        self.root.get_screen('module').ids.module_entry.text=''
        self.notice('Added to '+self.module_title)
    def _save_record_worker(self,kind,value):
        record_types={'tasks':'task','calendar':'event','bills':'bill','lists':'list','documents':'document','goals':'goal'}
        try:
            self.backend.save_record(record_types.get(kind,kind),{'text':value})
        except BackendError as exc:
            msg=str(exc)
            Clock.schedule_once(lambda _dt:self.notice('Cloud save failed: '+msg),0)
    def notice(self,msg):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        Popup(title='Pendo',content=Label(text=msg),size_hint=(.82,.28)).open()
if __name__=='__main__':
    PendoApp().run()