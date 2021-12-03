from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
import os
import csv
from kivy.metrics import dp
import requests;import json;import datetime;from datetime import timedelta
from kivymd.uix.label import MDLabel
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.lang import Builder

Builder.load_file("scroll_table_data.kv")
class ScrollViewForTable(ScrollView):...

class TableData(GridLayout):
    user_id_str: str
    email: str
    password: str
    url_get_activities='https://api.what-sticks-health.com/get_user_health_descriptions/'
    date_dict={}
    act_dict={}
    del_box_dict={}
    sort_direction:str
    def __init__(self,sort_direction,**kwargs):
        if 'sort_direction ' in kwargs:
            self.sort_direction = kwargs.pop('sort_direction')
        else:
            self.sort_direction = sort_direction
        super(TableData,self).__init__(**kwargs)
        self.get_table_data()
        self.add_data_to_table()
        print('TableData initialized')
        print('sort_direction::',self.sort_direction)

    def get_table_data(self):
        response = requests.request('GET',
            self.url_get_activities+str(self.user_id_str),
            auth=(self.email,self.password))
        # print('response in TableDAta:::',response.status_code)

        response_decoded=response.content.decode('utf-8')
        response_data=json.loads(response.content.decode('utf-8'))

        self.row_data_list=[(i['id'],self.convert_datetime(
            i['datetime_of_activity']),i['var_activity']) for i in response_data]
        # print('sort_direction::', self.sort_direction)
        if self.sort_direction=='ascending':
            # print('self.row_data_list:::',type(self.row_data_list))
            # print('self.row_dataPlist.sorted():::',self.row_data_list.sort())
            self.row_data_list.sort(key=lambda k: (k[1]))
            # print('triggerd if sort_direction::', self.row_data_list)
        if self.sort_direction=='descending':
            self.row_data_list.sort(reverse=True)

    def add_data_to_table(self):
        # self.row_data_list=self.get_table_data()

        for i in self.row_data_list[-20:]:
            date_time_obj=MDLabel(text=str(i[1]), size_hint=(None,None),
                size=(self.width*(1/3),dp(50)),
                font_size=10, padding=(dp(15),0))
            activity_obj=MDLabel(text=str(i[2]), size_hint=(None,None), size=(self.width*(1/3),dp(50)))
            del_box=RelativeLayout(size_hint=(None,None),size=(self.width*(1/3),dp(50)))
            delete_btn=Button(text=str(i[0]),font_size=2,color=(.5,.5,.5,0),
                size_hint=(.5,.5),
                pos_hint={'center_x':.5,'center_y':.5}
                )

            delete_btn.bind(on_press=self.delete_button_pressed)
            delete_label=MDLabel(text='delete',pos_hint={'x':.35})

            del_box.add_widget(delete_btn)
            del_box.add_widget(delete_label)
            self.date_dict[i[0]]=date_time_obj
            self.act_dict[i[0]]=activity_obj
            # self.del_dict[i[0]]=delete_btn
            self.del_box_dict[i[0]]=del_box
            self.add_widget(date_time_obj)
            self.add_widget(activity_obj)
            self.add_widget(del_box)
            # self.cols=3

    def delete_button_pressed(self,widget):
        # print('button preseed')
        # print('widget.text:',str(widget.text))
        AreYouSureBox.activity_id_str=str(widget.text)
        AreYouSureBox.email=self.email
        AreYouSureBox.password=self.password
        self.parent.parent.parent.parent.parent.parent.add_widget(AreYouSureBox())
        # print('self.parent:::',self.parent)
        # print('self.parent.parent:::',self.parent.parent)
        # print('self.parent.parent.parent.parent.parent.parent.:::',
        # self.parent.parent.parent.parent.parent.parent)

    def on_size(self, *args):
        width_size=self.width
        for i,j in self.date_dict.items():
            j.width=width_size*(1/3)
            # if len(j.text)>15:
            j.font_size=12
        for i,j in self.act_dict.items():
            j.width=width_size*(1/3)
            if len(j.text)>15:
                j.font_size=12
        for i,j in self.del_box_dict.items():
            j.width=width_size*(1/3)

    def convert_datetime(self,date_time_str):
        try:
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
        # return date_time_obj.strftime("%m/%d/%Y, %H:%M:%S")
        return date_time_obj.strftime("%b%-d '%-y %-I:%M%p")#<------Potential hangup!***************!



class AreYouSureBox(BoxLayout):
    activity_id_str=''
    email=''
    password=''
    url='https://api.what-sticks-health.com/get_health_descriptions/'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app=MainApp.get_running_app()
    def yes_button(self):

        response = requests.request('DELETE',self.url+self.activity_id_str, auth=(self.email,self.password))
        # print('response:::',response.status_code)
        self.parent.remove_widget(self)
        self.app.ps2.csm.current="activity_screen"
        self.app.ps2.csm.current="table_screen"

        # self.parent.remove_widget(self)
        # self.parent.remove_widget(parent)
    def no_button(self):
        self.parent.remove_widget(self)
