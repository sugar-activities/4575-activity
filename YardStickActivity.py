# Copyright 2011-2012 Almira Cayetano
# Copyright 2011-2012 Christian Joy Aranas
# Copyright 2011-2012 Ma. Rowena Solamo
# Copyright 2011-2012 Rommel Feria
# Copyright 2007-2008 One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# This program is a project of the University of the Philippines, College
# of Engineering, Department of Computer Science intended for
# educational purposes. If you have any suggestions and comments, you can contact us
# with the following email addresses :
#
# Almira Cayetano - accayetano@ittc.up.edu.ph
# Christian Joy Aranas - cjmaranas@gmail.com
# Ma. Rowena Solamo - rcsolamo@dcs.upd.edu.ph
# Rommel Feria - rpferia@dcs.upd.edu.ph

import pygtk
pygtk.require('2.0')
import gtk, gobject
from Models import*
from Template import Template
from Bundler import Bundler
import datetime
import pango
import hippo
import logging
import telepathy

import cjson
import logging
import telepathy
from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

from sugar.activity.activity import Activity, ActivityToolbox
from sugar.activity import activity
from sugar.graphics import style
from sugar.graphics.alert import NotifyAlert
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

from telepathy.interfaces import (
    CHANNEL_INTERFACE, CHANNEL_INTERFACE_GROUP, CHANNEL_TYPE_TEXT,
    CONN_INTERFACE_ALIASING)
from telepathy.constants import (
    CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES,
    CHANNEL_TEXT_MESSAGE_TYPE_NORMAL)
from telepathy.client import Connection, Channel

SERVICE = "org.laptop.YardStick"
IFACE = SERVICE
PATH = "/org/laptop/YardStick"


BORDER_COLOR = '#FFDE00'
BACKGROUND_COLOR = '#66CC00'
BUTTON_COLOR = '#097054'
WHITE = '#FFFFFF'
BLUE = '#82CAFA'
PINK = '#FF0198'

restrictions_level = ["2", "3", "4", "5", "6", "7", "8", "9"]
restrictions_category = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
RUBRICTITLE = []
RUBRICLIST = []


def theme_button(button):
    
    button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLUE))  
    return button

def image_button(button, path):
    pixbufanim = gtk.gdk.PixbufAnimation(path)
    image = gtk.Image()
    image.set_from_animation(pixbufanim)
    image.show()
    button.add(image)
    return button

def theme_box(box, color):
    eb = gtk.EventBox()
    box.set_border_width(5)
    eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(color))
    eb.add(box)
    
    return eb

class YardStickActivity(activity.Activity):
#class YardStickActivity():
    def __init__(self, handle):
#    def __init__(self):
        logging.root.setLevel(logging.DEBUG)
        Activity.__init__(self, handle)
        self.set_title('YardStick Activity')

        toolbox = ActivityToolbox(self)
        self.set_toolbox(toolbox)
        toolbox.show()

        self.pservice = presenceservice.get_instance()

        owner = self.pservice.get_owner()
        self.owner = owner
        self.owner_nick = owner.props.nick
        self.is_exists = False
        self.overwrite = False
        self.current_category_id = None
#        self.owner_nick = "cnix"
        
        self.yardstickDB = YardStickDB()
        is_newlycreated = self.yardstickDB.connect_db(self.owner_nick)
        if(is_newlycreated):
            template = Template(self.owner_nick, self.yardstickDB)
            logging.debug("ScorepadDB --> template")
            template.save_template()
            logging.debug("ScorepadDB -->save_template")
              
        list = self.yardstickDB.queryall_rubric(1)
        
        for temp in list:
            RUBRICLIST.append(temp)
            RUBRICTITLE.append(temp.title)          
        
        list = self.yardstickDB.queryall_rubric(0)
        
        for temp in list:
            RUBRICLIST.append(temp)
            RUBRICTITLE.append(temp.title)

        self.main_table_eb = gtk.EventBox()
        self.main_table = gtk.Table(1,3,True)
        self.main_table_eb.add(self.main_table)	
        self.main_table_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        self.main_table_eb.set_border_width(20)
        
        self.rubric_box = gtk.Table(12,3, True)
        self.processpanel = gtk.Frame()
        self.processpanel.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        self.processpanel.set_border_width(10)
        self.processpanel.set_label("Welcome to YardStick!")
        logo = gtk.Image()
        logo.set_from_file("images/homepage.png")
        logo.show()
        self.rubric_box.attach(logo,0,3,0,12)
        
        self.processpanel.add(self.rubric_box)
        
        self.hpaned_window = gtk.HPaned()
        self.hpaned_window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        
        self.left_hpaned = self.create_rubric_list()
        self.hpaned_window.add1(self.left_hpaned)
        self.hpaned_window.set_position(270)
        
        self.hpaned_window.add2(self.processpanel)
        
        self.main_event_box = gtk.EventBox()
        self.main_event_box.add(self.hpaned_window)
        self.main_event_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        self.main_event_box.show_all()
        self.set_canvas(self.main_event_box)
        
        
        self.is_shared = False
        self.text_channel = None
        if self.shared_activity:
            logging.debug('Activity joined')
            self.connect('joined', self._joined_cb)
            if self.get_shared():
                self._joined_cb(self)
        else:
            logging.debug('Activity shared')
            self.connect('shared', self._shared_cb)

#        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
#        self.window.set_title("YardStick")
#        self.window.resize(730,650)
#        self.window.add(self.main_event_box)
#        self.window.show_all()

    def load_window(self):
        self.left_hpaned.destroy()
        self.left_hpaned = self.create_rubric_list()
        self.hpaned_window.add1(self.left_hpaned)

        self.processpanel.set_label("Welcome to YardStick!")
        
        logo = gtk.Image()
        logo.set_from_file("images/homepage.png")
        logo.show()

        self.rubric_box.attach(logo,0,3,0,12)
        self.processpanel.add(self.rubric_box)
        
        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()
        
    def create_rubric_list(self):
        rubric_list_table = gtk.Table(12,1,True)
        
        tree_store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        
        count = 0
        for r in RUBRICTITLE:
            tree_store.append(None, (r + " - " +str(RUBRICLIST[count].author),None))
            count = count+1
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_border_width(5)
        
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        self.tree_view = gtk.TreeView(tree_store)
        
        scrolled_window.add_with_viewport (self.tree_view)
        self.tree_view.show()
        
        self.cell = gtk.CellRendererText()
        
        self.column = gtk.TreeViewColumn("Rubrics List", self.cell, text=0)
        
        self.tree_view.append_column(self.column)

        share_button = gtk.Button()
        share_button = image_button(share_button,"images/share.png")
        share_button = theme_button(share_button)
        
        box = gtk.HBox(False,2)
        new_rubric_button = gtk.Button()
        new_rubric_button = image_button(new_rubric_button,"images/addnew.png")
        new_rubric_button = theme_button(new_rubric_button)
        new_rubric_button.connect("clicked", self.enter_row_column, "Rubric")
        box.add(new_rubric_button)
        box = theme_box(box,BUTTON_COLOR)
        
        rubric_list_table.attach(box,0,1,11,12)
        
        logo = gtk.Image()
        logo.set_from_file("images/YardStick.png")
        logo.show()
        
        self.tree_view.connect("row-activated", self.view_rubric_details)
        self.tree_view.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLUE))
        rubric_list_table.attach(logo, 0,1,0,4)
        
        rubric_list_table.attach(scrolled_window,0,1,4,11)
        rubric_list_table.show_all()
        scrolled_window.show_all()
        
        return rubric_list_table
        
    def view_rubric_details(self,widget,row,col):
        r = row[0]
        self.selected_rubric = r
        rubric = RUBRICLIST[r] 
        rubric_id = RUBRICLIST[r].rubric_id
        print "almira"+str(RUBRICLIST[r].rubric_id)
        self.selected_rubric_id = rubric_id
        category = self.yardstickDB.queryall_category(rubric_id) 
        category_id = category[0].category_id
        row = len(category)+1
        
        c = len(self.yardstickDB.query_level(category_id))+1      
        column_names = self.yardstickDB.query_level(category_id)
        level_names = []
        
        for i in column_names:
            level_names.append(i.name)
        
        levels = []
                    
        for i in range(c-1):
            level = []
            for j in range(row-1):
                category_id = category[j].category_id
                level_temp = self.yardstickDB.query_level(category_id)
                level.append(level_temp[i].description)                    
            levels.append(level)
        
        tree_store = self.create_tree_store(c)
        
        column = []
        
        for i in range(len(levels)):
            column.append(levels[i])
        
        rubric_id = rubric.rubric_id    
        category = self.yardstickDB.queryall_category(rubric_id)    
        tuple = []
        for i in range(len(category)):
            tuple = []
            tuple.append(category[i].name + " (" + str(category[i].percentage) + ")")
            
            for j in range(c-1):
                tuple.append(column[j][i])
           
            tree_store.append(None, tuple)

        view = gtk.TreeView(tree_store)
        view.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLUE))
        view.set_rules_hint(True)    
        renderer = gtk.CellRendererText()
        renderer.props.wrap_width = 100
        renderer.props.wrap_mode = pango.WRAP_WORD
        column0 = gtk.TreeViewColumn("Category", renderer, text=0)
        column0.set_resizable(True)
        view.append_column(column0)
        
        for i in range(len(levels)):
            render = gtk.CellRendererText()
            render.props.wrap_width = 100
            render.props.wrap_mode = pango.WRAP_WORD
            column = gtk.TreeViewColumn(column_names[i].name + " (" + str(column_names[i].points) + ")", render, text=i+1)
            column.set_resizable(True)
            view.append_column(column)

        hbox = gtk.HBox(False, 2)
        self.rubric_title_copy = rubric.title
        
        edit_button = gtk.Button()
        edit_button = image_button(edit_button,"images/edit.png")
        edit_button = theme_button(edit_button)
        edit_button.connect("clicked", self.edit_rubric, rubric, r, row, c, level_names, levels)
        hbox.add(edit_button)
        
        delete_button = gtk.Button()
        delete_button = image_button(delete_button,"images/delete.png")
        delete_button = theme_button(delete_button)
        delete_button.connect("clicked", self.delete_rubric, rubric, r)
        hbox.add(delete_button)

        share_button = gtk.Button()
        share_button = image_button(share_button,"images/share.png")
        share_button = theme_button(share_button)
        share_button.connect("clicked", self.share_cb)
        hbox.add(share_button)        

        send_sp = gtk.Button()
        send_sp = image_button(send_sp,"images/sendtoscorepad.png")
        send_sp = theme_button(send_sp)
        send_sp.connect("clicked", self.send_to_ScorePad)
        hbox.add(send_sp)
        
        hbox = theme_box(hbox, BUTTON_COLOR)

        author_img = gtk.Image()
        author_img.set_from_file("images/author.png")
        author_text = gtk.Entry()
        author_text.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        author_text.set_text(rubric.author)
        
        description_img = gtk.Image()
        description_img.set_from_file("images/description.png")
        description_text = gtk.Entry()
        description_text.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        description_text.set_text(rubric.description)
        
        vbox1 = gtk.VBox(False,2)
        vbox1.add(author_img)
        vbox1.add(description_img)
        
        vbox2 = gtk.VBox(False,2)
        vbox2.add(author_text)
        vbox2.add(description_text)
            
        box = view
        box = theme_box(box,BACKGROUND_COLOR)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(box)
        sw.set_border_width(5)
        
        self.processpanel.destroy()
        
        design = gtk.Image()
        design.set_from_file("images/child.png")
        
        self.view_rubric_table = gtk.Table(12,3,True)
        self.view_rubric_table.attach(vbox1,0,1,0,2)
        self.view_rubric_table.attach(vbox2,1,2,0,2)
        self.view_rubric_table.attach(design,2,3,0,2)
        self.view_rubric_table.attach(sw,0,3,2,11)
        self.view_rubric_table.attach(hbox,0,3,11,12)
        
        self.processpanel.add(self.view_rubric_table)
        self.processpanel.set_label(rubric.title + " Details")
        
        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()
        
    def edit_rubric(self, widget, rubric, r, row, column, levels, level_description):

        title_img = gtk.Image()
        title_img.set_from_file("images/title.png")
        author_img = gtk.Image()
        author_img.set_from_file("images/author.png")
        self.title_entry = gtk.Entry(50)
        self.title_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.title_entry.set_text(rubric.title)
        self.author_entry = gtk.Entry(50)
        self.author_entry.set_text(rubric.author)
        self.author_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.description_field = gtk.TextView()
        self.description_field.set_wrap_mode(gtk.WRAP_WORD)
        df_buffer = self.description_field.get_buffer()
        df_buffer.set_text(rubric.description)
        self.description_field.set_border_width(3)
        self.description_field.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BUTTON_COLOR))
        df_sw = gtk.ScrolledWindow()
        df_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        df_sw.add_with_viewport(self.description_field)
        
        self.category_entries = []
        self.level_entries = []
        self.text_entries = []
        
        hbox = gtk.HBox(False,2)
        
        self.checkbox = gtk.CheckButton("Enable Points")
        self.checkbox =  theme_button(self.checkbox)
        
        is_enabled = self.yardstickDB.is_points_enabled(rubric.rubric_id)
        self.checkbox.set_active(is_enabled)
        self.checkbox.connect("clicked", self.enable_points)
        self.rubric_box.attach(self.checkbox,0,1,11,12)
        
        self.points_button = gtk.Button()
        self.points_button = image_button(self.points_button,"images/editpoints.png")
        
        if is_enabled :
            self.points_button.set_sensitive(True)
        else:
            self.points_button.set_sensitive(False)
        self.points_button = theme_button(self.points_button)
        hbox.add(self.points_button)
        
        self.update_button = gtk.Button()
        self.update_button = image_button(self.update_button,"images/update.png")
        self.update_button = theme_button(self.update_button)
        self.update_button.connect("clicked", self.update_warning, rubric, r)
        hbox.add(self.update_button)
        
        hbox = theme_box(hbox, BUTTON_COLOR)

        self.rubric_text_view_table = gtk.Table((row*5)+1,(column*5)+1,True)
        rubric_text_eb = gtk.EventBox()
        rubric_text_eb.add(self.rubric_text_view_table)    
        rubric_text_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        
        categories = self.yardstickDB.queryall_category(rubric.rubric_id)
        category_names = []
        category_ids = []    
        description = []
            
        for i in categories:
            category_names.append(i.name)
            category_ids.append(i.category_id)
        
        for i in category_ids:
            level = self.yardstickDB.query_level(i)
            
            for j in level:
                description.append(j.description)
        
        self.points_button.connect("clicked", self.points_cb, rubric, categories, level)
        
        left = 1
        right = 5
        up = 1
        down = 5
        level_counter = 0
        category_counter = 0
        description_counter = 0
        for i in range(row):
            for j in range(column):
                
                if i == 0 and j == 0:
                    self.level_label = gtk.Label("Level")
                    self.category_label = gtk.Label("Category")
                    self.rubric_text_view_table.attach(self.level_label,1,5,1,3)
                    self.rubric_text_view_table.attach(self.category_label,1,5,3,5)
                    left += 5
                    right += 5    
                elif i == 0:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    buffer.set_text(levels[level_counter])
                    level_counter += 1
                    self.level_entries.append(buffer)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(PINK))
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_NEVER)
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5
                elif j == 0:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    buffer.set_text(category_names[category_counter])
                    category_counter += 1
                    self.category_entries.append(buffer)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(PINK))
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_NEVER)
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5                        
                else:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    buffer.set_text(description[description_counter])
                    description_counter += 1
                    self.text_entries.append(buffer)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BUTTON_COLOR))
                    temp.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(BLUE))
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_NEVER)
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5
            left = 1
            right = 5
            up += 5
            down += 5
        
        self.rubricVB1 = gtk.VBox(False,0)
        self.rubricVB2 = gtk.VBox(False,0)
    
        self.processpanel.destroy()
        self.processpanel.add(self.rubric_box)
        self.processpanel.set_label("Rubric Maker")
        
        self.rubricVB1.add(title_img)
        self.rubricVB1.add(author_img)
        
        description_frame = gtk.Frame()
        description_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        description_frame.set_border_width(5)
        description_frame.set_label("Description")
        description_frame.add(df_sw)
        
        self.rubricVB2.add(self.title_entry)
        self.rubricVB2.add(self.author_entry)
        
        self.rubric_box.attach(self.rubricVB1, 0,1,0,2)
        self.rubric_box.attach(self.rubricVB2, 1,2,0,2)
        self.rubric_box.attach(description_frame,2,3,0,2)
        self.rubric_box.attach(hbox, 1,3,11,12)
        
        sw_eb = gtk.EventBox()
        
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled_window.add_with_viewport(rubric_text_eb)
        self.scrolled_window = theme_box(self.scrolled_window, BORDER_COLOR)
        
        sw_eb.add(self.scrolled_window)
        self.rubric_box.attach(sw_eb, 0,3,2,11)
        
        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()
        
    def points_cb(self,widget,rubric, categories,levels):
        title_img = gtk.Image()
        title_img.set_from_file("images/title.png")
        author_img = gtk.Image()
        author_img.set_from_file("images/author.png")
        self.title_entry = gtk.Entry(50)
        self.title_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.title_entry.set_text(rubric.title)
        self.author_entry = gtk.Entry(50)
        self.author_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.author_entry.set_text(rubric.author)
        self.description_field = gtk.TextView()
        self.description_field.set_wrap_mode(gtk.WRAP_WORD)
        df_buffer = self.description_field.get_buffer()
        df_buffer.set_text(rubric.description)
        self.description_field.set_border_width(3)
        self.description_field.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BUTTON_COLOR))
        df_sw = gtk.ScrolledWindow()
        df_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        df_sw.add_with_viewport(self.description_field)
        
        self.rubricVB1 = gtk.VBox(False,0)
        self.rubricVB2 = gtk.VBox(False,0)
    
        self.processpanel.destroy()
        self.processpanel.add(self.rubric_box)
        self.processpanel.set_label("Rubric Maker")
        
        self.rubricVB1.add(title_img)
        self.rubricVB1.add(author_img)
        
        description_frame = gtk.Frame()
        description_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        description_frame.set_border_width(5)
        description_frame.set_label("Description")
        description_frame.add(df_sw)
        
        self.rubricVB2.add(self.title_entry)
        self.rubricVB2.add(self.author_entry)
        
        self.rubric_box.attach(self.rubricVB1, 0,1,0,2)
        self.rubric_box.attach(self.rubricVB2, 1,2,0,2)
        self.rubric_box.attach(description_frame,2,3,0,2)

        self.level_attr = []
        self.category_attr = []
        
        middlebox = gtk.HBox(False,20)
        middlebox.add(self.build_pointbox(levels, 0))
        middlebox.add(self.build_pointbox(categories, 1))
        middlebox = theme_box(middlebox, BLUE)
        self.rubric_box.attach(middlebox,0,3,3,11)
        
        img_box = gtk.HBox(False,20)
        level_img = gtk.Image()
        level_img.set_from_file("images/levels.png")
        category_img = gtk.Image()
        category_img.set_from_file("images/categories.png")
        img_box.add(level_img)
        img_box.add(category_img)
        img_box = theme_box(img_box, BLUE)
        
        self.rubric_box.attach(img_box,0,3,2,3)
        
        hbox = gtk.HBox(False,2)
        
        save_points_button = gtk.Button()
        save_points_button = image_button(save_points_button,"images/save.png")
        save_points_button = theme_button(save_points_button)
        save_points_button.connect("clicked", self.save_points, rubric.rubric_id)
        hbox.add(save_points_button)
        hbox = theme_box(hbox, BUTTON_COLOR)
        self.rubric_box.attach(hbox, 2,3,11,12)

        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()  
        
        
    def enable_points(self, widget, data=None):
        if self.checkbox.get_active():
            self.points_button.set_sensitive(True)
        else:
            self.points_button.set_sensitive(False)
        
    
    def build_pointbox(self, elements, checker):
        label_vbox = gtk.VBox(False,0)
        spinner_vbox = gtk.VBox(False,0)
        count = len(elements)
        equal_percentage = 100.0/count

        for element in elements:
            label_temp = gtk.Label(element.name)
            label_vbox.add(label_temp)
            if checker == 0:
                initial = element.points
            else:
                initial = element.percentage
                if initial == 0.0:
                    initial = equal_percentage
                
            adj = gtk.Adjustment(initial,1,100,10,0,0)
            spinner = gtk.SpinButton(adj, 0, 0)
            spinner.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BLUE))
            spinner.set_wrap(True)
            spinner_vbox.add(spinner)
            if checker == 0:
                tuple = (element.name, spinner)
                self.level_attr.append(tuple)
            else:
                tuple = (element.category_id, spinner)
                self.category_attr.append(tuple)
        hbox = gtk.HBox(False,0)
        hbox.add(label_vbox)
        hbox.add(spinner_vbox)
        
        return hbox
    
    def save_points(self, widget, rubric_id):
        
        percent = 0
        for attr in self.category_attr:
            id = attr[0]
            spinner = attr[1]
            percent = percent + spinner.get_value_as_int()
        
        if percent > 100 or percent < 100:
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                                       flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                                       type = gtk.MESSAGE_INFO,\
                                       message_format = "Total percentage must exactly be 100%")
            md.run()
            md.destroy()
        else:
            self.yardstickDB.update_enablepoints(rubric_id,1)
            for attr in self.category_attr:
                id = attr[0]
                spinner = attr[1]
                self.yardstickDB.update_percentage(id, spinner.get_value_as_int())
                for attr2 in self.level_attr:
                    name = attr2[0]
                    spinner2 = attr2[1]
                    self.yardstickDB.update_points(id, name, spinner2.get_value_as_int())

            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                                       flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                                       type = gtk.MESSAGE_INFO,\
                                       message_format = "Points saved!")
            md.run()
            md.destroy()
            self.processpanel.destroy()
            self.load_window()
        
        
    def update_warning(self, widget, rubric, r):
        warning = gtk.MessageDialog(parent = None,buttons = gtk.BUTTONS_YES_NO, \
                                    flags =gtk.DIALOG_DESTROY_WITH_PARENT,\
                                    type = gtk.MESSAGE_WARNING,\
                                    message_format = "Are you sure you want to save changes?")
        result = warning.run()
        
        if(result == gtk.RESPONSE_YES):
            count = self.yardstickDB.rubric_title_exists(self.title_entry.get_text())
            warning.destroy()
            if(count == None):
                self.update_rubric(widget,rubric,r)
                self.processpanel.destroy()
                self.load_window()
                print "Count if"
            else:
                print self.title_entry.get_text() + "       " + self.rubric_title_copy
                if(self.title_entry.get_text() == self.rubric_title_copy):
                    self.update_rubric(widget,rubric,r)
                    self.processpanel.destroy()
                    self.load_window()
                    print "Count else title if"
                else:
                    warning2 = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                                           flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                                           type = gtk.MESSAGE_INFO,\
                                           message_format = "Name already exists. Please rename the rubric.")
                    result = warning2.run()
                    warning2.destroy()    
        elif(result == gtk.RESPONSE_NO):
            warning.destroy()
        warning.destroy()
        
    def update_rubric(self,widget,orig_rubric,r):

        title = self.title_entry.get_text()
        author = self.author_entry.get_text()
        description_buffer = self.description_field.get_buffer()
        start = description_buffer.get_start_iter()
        end = description_buffer.get_end_iter()
        description = description_buffer.get_text(start,end,True)
        
        self.get_texts()
        #self.processpanel.destroy()

        if self.checkbox.get_active():
            enable_points = 1
        else :
            enable_points = 0
        
        rubric = Rubric(orig_rubric.rubric_id, title, author, description, 0, self.owner_nick, "",enable_points)
        self.yardstickDB.update_rubric(rubric)
        rubric = self.yardstickDB.query_rubric(orig_rubric.rubric_id)

        RUBRICTITLE[r] = rubric.title
        RUBRICLIST[r] = rubric
        
        level = []
        category_id_retrieve = []
        
        temporary = self.yardstickDB.queryall_category(orig_rubric.rubric_id) 
        
        for i in temporary:
            category_id_retrieve.append(i.category_id)
            
        level_id_retrieve = []
        
        for i in category_id_retrieve:
            
            temporary = self.yardstickDB.query_level(i)
        
            for j in temporary:
                level_id_retrieve.append(j.level_id)
        
        for i in self.levels:
            temp = Level()
            temp.name = i
            temp.rubric_id = orig_rubric.rubric_id
            level.append(temp)

        counter = 0
        category_counter = 0
        level_counter = 0
        category_array = []
        
        for i in self.categories:
            for k in level:
                k.description = self.criteria_description[counter]
                counter += 1
                k.category_id = category_id_retrieve[category_counter]
                k.level_id = level_id_retrieve[level_counter]
                level_counter += 1

            category = Category()                
            category.name = i
            category.description = "NONE"
            category.rubric_id = orig_rubric.rubric_id
            category.category_id = category_id_retrieve[category_counter]
            category_counter += 1
            category_array.append(category)    
            self.yardstickDB.update_levels(level)
        self.yardstickDB.update_categories(category_array) 
        #self.load_window()
        
    def delete_rubric(self, widget, rubric, r):     
        
        warning = gtk.MessageDialog(parent = None,buttons = gtk.BUTTONS_YES_NO, \
                                    flags =gtk.DIALOG_DESTROY_WITH_PARENT,\
                                    type = gtk.MESSAGE_WARNING,\
                                    message_format = "Are you sure you want to delete the rubric?")
        result = warning.run()
        rubric_id = rubric.rubric_id
        
        if result == gtk.RESPONSE_YES:
            RUBRICTITLE.remove(rubric.title)
            RUBRICLIST.remove(rubric)
            self.yardstickDB.delete_rubric(rubric_id)
            warning.destroy()
            self.processpanel.destroy()
            self.load_window()
        elif result == gtk.RESPONSE_NO:
            warning.destroy()
        warning.destroy()        
        
    def create_tree_store(self, c):
        
        if c == 2:
            p = gtk.TreeStore(str,str)
        elif c == 3:
            p = gtk.TreeStore(str,str,str)
        elif c == 4:
            p = gtk.TreeStore(str,str,str,str)
        elif c == 5:
            p = gtk.TreeStore(str,str,str,str,str)
        elif c == 6:
            p = gtk.TreeStore(str,str,str,str,str,str)
        elif c == 7:
            p = gtk.TreeStore(str,str,str,str,str,str,str)
        elif c == 8:
            p = gtk.TreeStore(str,str,str,str,str,str,str,str)
        elif c == 9:
            p = gtk.TreeStore(str,str,str,str,str,str,str,str,str)
        return p
        
    def enter_row_column(self,widget,label):
        
        self.processpanel.destroy()
        self.processpanel.set_label("Enter number of categories and levels")
        
        self.rc_table = gtk.Table(8,3, True)
        
        level_label = gtk.Label("Levels")
        category_label = gtk.Label("Categories")
        
        level_adj = gtk.Adjustment(2,2,9,1,0,0)
        level_spinner = gtk.SpinButton(level_adj, 0, 0)
        level_spinner.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        level_spinner.set_wrap(True)
        
        category_adj = gtk.Adjustment(1,1,9,1,0,0)
        category_spinner = gtk.SpinButton(category_adj, 0, 0)
        category_spinner.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        category_spinner.set_wrap(True)
        
        submit_button = gtk.Button()
        submit_button = image_button(submit_button,"images/submit.png")
        submit_button = theme_button(submit_button)
        submit_button.connect("clicked", self.add_rubric, category_spinner, level_spinner)
        
        vbox1 = gtk.VBox(False,2)
        vbox2 = gtk.VBox(False,2)
        
        button_table = gtk.Table(2,1,True)
        button_table.attach(submit_button, 0,1,0,1)
        
        vbox1.add(level_label)
        vbox1.add(category_label)
                
        vbox2.add(level_spinner)
        vbox2.add(category_spinner)
        
        self.rc_table.attach(vbox1,0,1,3,4)
        self.rc_table.attach(vbox2,1,2,3,4)
        self.rc_table.attach(button_table,1,2,4,5)
        
        self.processpanel.add(self.rc_table)
        
        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()
        
    def add_rubric(self,widget,r,c):
        self.title_label = gtk.Label("Rubric Title")
        self.author_label = gtk.Label("Author")
        self.title_entry = gtk.Entry(50)
        self.title_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.author_entry = gtk.Entry(50)
        self.author_entry.modify_bg(gtk.STATE_INSENSITIVE,gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.description_field = gtk.TextView()
        self.description_field.set_wrap_mode(gtk.WRAP_WORD)
        self.description_field.set_border_width(3)
        self.description_field.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BUTTON_COLOR))
        df_sw = gtk.ScrolledWindow()
        df_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        df_sw.add_with_viewport(self.description_field)
        
        self.category_entries = []
        self.level_entries = []
        self.text_entries = []
        
        hbox = gtk.HBox(False, 2)
        
        self.finalize_button = gtk.Button()
        self.finalize_button = image_button(self.finalize_button,"images/finalize.png")
        self.finalize_button = theme_button(self.finalize_button)
        self.finalize_button.connect("clicked", self.finalize_cb)
        hbox.add(self.finalize_button)
        hbox = theme_box(hbox, BUTTON_COLOR)
        
        row = r.get_value_as_int() + 1
        column = c.get_value_as_int() + 1
        self.rubric_text_view_table = gtk.Table((row*5)+1,(column*5)+1,True)
        rubric_text_eb = gtk.EventBox()
        rubric_text_eb.add(self.rubric_text_view_table)    
        rubric_text_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        
        left = 1
        right = 5
        up = 1
        down = 5
        
        for i in range(row):
            for j in range(column):
                
                if i == 0 and j == 0:
                    self.level_label = gtk.Label("Level")
                    self.category_label = gtk.Label("Category")
                    self.rubric_text_view_table.attach(self.level_label,1,5,1,3)
                    self.rubric_text_view_table.attach(self.category_label,1,5,3,5)
                    left += 5
                    right += 5    
                elif i == 0:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    self.level_entries.append(buffer)
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(PINK))
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5
                elif j == 0:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    self.category_entries.append(buffer)
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(PINK))
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5                        
                else:
                    temp = gtk.TextView()
                    temp.set_wrap_mode(gtk.WRAP_WORD)
                    buffer = temp.get_buffer()
                    self.text_entries.append(buffer)
                    sw = gtk.ScrolledWindow()
                    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)
                    temp.set_border_width(3)
                    temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BUTTON_COLOR))
                    temp.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(BLUE))
                    sw.add(temp)
                    self.rubric_text_view_table.attach(sw, left, right, up, down)
                    left += 5
                    right += 5
            left = 1
            right = 5
            up += 5
            down += 5
        
        self.rubricVB1 = gtk.VBox(False,3)
        self.rubricVB2 = gtk.VBox(False, 3)
        
        self.processpanel.destroy()
        self.processpanel.add(self.rubric_box)
        self.processpanel.set_label("Rubric Maker")
        self.processpanel.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        self.processpanel.set_border_width(5)
        
        self.rubricVB1.add(self.title_label)
        self.rubricVB1.add(self.author_label)
        
        description_frame = gtk.Frame()
        description_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(BACKGROUND_COLOR))
        description_frame.set_border_width(5)
        description_frame.set_label("Description")
        description_frame.add(df_sw)
        
        self.rubricVB2.add(self.title_entry)
        self.rubricVB2.add(self.author_entry)
        
        self.rubric_box.attach(self.rubricVB1, 0,1,0,2)
        self.rubric_box.attach(self.rubricVB2, 1,2,0,2)
        self.rubric_box.attach(description_frame,2,3,0,2)
        self.rubric_box.attach(hbox,2,3,11,12)
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolled_window.add_with_viewport(rubric_text_eb)
        scrolled_window.set_border_width(5)
        scrolled_window = theme_box(scrolled_window, BORDER_COLOR)
        
        self.rubric_box.attach(scrolled_window, 0,3,2,11)
        
        self.hpaned_window.add2(self.processpanel)
        self.hpaned_window.show_all()
        
    def get_texts(self):
        
        self.categories = []
        self.levels = []
        self.criteria_description = []
        
        for i in self.category_entries:
            start, end = i.get_bounds()
            text = i.get_slice(start,end, True)
            self.categories.append(text)
                
        for i in self.level_entries:
            start, end = i.get_bounds()
            text = i.get_text(start,end, True)
            self.levels.append(text)
            
        for i in self.text_entries:
            start, end = i.get_bounds()
            text = i.get_text(start,end, True)
            self.criteria_description.append(text)
        
    def finalize_cb(self, widget):
        
        rubric_id = self.yardstickDB.query_maxrubric() + 1
        title = self.title_entry.get_text()
        author = self.author_entry.get_text()
        description_buffer = self.description_field.get_buffer()
        start = description_buffer.get_start_iter()
        end = description_buffer.get_end_iter()
        description = description_buffer.get_text(start,end,True)

        self.get_texts()
        rubric = Rubric(None, title, author, description, 0, self.owner_nick, "",0)
        count = self.yardstickDB.rubric_title_exists(rubric.title)
        
        if(count == None):
            self.yardstickDB.insert_rubric(rubric)
            rubric_id = self.yardstickDB.query_maxrubric()
            rubric = self.yardstickDB.query_rubric(rubric_id)
            RUBRICLIST.append(rubric)
            RUBRICTITLE.append(rubric.title)
        
            counter = 0
            for i in self.categories:
                levels = []
                category = Category(None, i, rubric_id, "", 0.0)
                for j in self.levels:
                    level = Level(None, j, self.criteria_description[counter], None, rubric_id, "", 0)
                    counter += 1
                    levels.append(level)
                self.yardstickDB.insert_criteria(category, levels)
            self.processpanel.destroy()
            self.load_window()  
        else:
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                               flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                               type = gtk.MESSAGE_INFO,\
                               message_format = "Name already exists. Please rename the rubric.")
            md.run()
            md.destroy()
        
    def send_to_ScorePad(self, widget):
        rubric = RUBRICLIST[self.selected_rubric]
        categories = []
        categories = self.yardstickDB.queryall_category(self.selected_rubric_id)
        levels = []
        
        self.yardstickDB.close_db()
        
        self.scorepadDB = ScorePadDB(self.owner_nick)
            
        if(self.scorepadDB.rubric_exists(rubric.title, rubric.author)==None):
            self.scorepadDB.insert_rubric(rubric)
            rubric_id = self.scorepadDB.query_maxrubric()
            self.scorepadDB.close_db()

            for category in categories:
                self.yardstickDB = YardStickDB()
                self.yardstickDB.connect_db(self.owner_nick)
                levels = self.yardstickDB.query_level(category.category_id)
                self.yardstickDB.close_db()
                self.scorepadDB = ScorePadDB(self.owner_nick)
                self.scorepadDB.insert_criteria2(category,levels,rubric_id)
                self.scorepadDB.close_db()
            
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                               flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                               type = gtk.MESSAGE_INFO,\
                               message_format = "Rubric sucessfully inserted")
            md.run()
            md.destroy()
        else:
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                               flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                               type = gtk.MESSAGE_INFO,\
                               message_format = "Rubric exists. Please rename the rubric title.")
            md.run()
            md.destroy()
    
        self.yardstickDB = YardStickDB()
        self.yardstickDB.connect_db(self.owner_nick)

    def share_cb(self,widget,data=None):
        
        if self.is_shared :
            rubric = RUBRICLIST[self.selected_rubric]
            rubric = self.yardstickDB.query_rubric(rubric.rubric_id)
            logging.debug("EP : "+str(rubric.enable_points))
            logging.debug("Rubric shared")
            bundler = Bundler()
            rubric_bundle = bundler.bundle_rubric(rubric)
            categories = self.yardstickDB.queryall_category(rubric.rubric_id)
            category_bundle = bundler.bundle_category(categories)
            level_bundle_list = []
            for category in categories:
                levels = self.yardstickDB.query_level(category.category_id)
                level_bundle = bundler.bundle_level(levels)
                level_bundle_list.append(level_bundle)
         
            self.sendbundle_cb(rubric_bundle)
            for i in range(len(category_bundle)):
                self.sendbundle_cb(category_bundle[i])
                level_temp = level_bundle_list[i]
                for level in level_temp:
                    logging.debug('Function: share_cb --> levelbundle sent')
                    self.sendbundle_cb(level)
            
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                              flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                              type = gtk.MESSAGE_INFO,\
                              message_format = "Rubric shared")
            md.run()
            md.destroy()
        else:
            md = gtk.MessageDialog(parent = None, buttons = gtk.BUTTONS_OK, \
                               flags = gtk.DIALOG_DESTROY_WITH_PARENT, \
                               type = gtk.MESSAGE_INFO,\
                               message_format = "Cannot share. You are not connected to anybody.")
            md.run()
            md.destroy()
        
#    def destroy(self, widget, data=None):
#        gtk.main_quit()
        
#    def main(self):
#        gtk.main()

    
#if __name__ == "__main__":
#    yardStick = YardStickActivity()
#    yardStick.main() 
        
    def update_status(self, nick, text):
        text = text.split("|")
        model_name = text[0]

        if model_name == "Rubric":
            self._alert("A Rubric was shared by", nick)
            rubric = Rubric(None, text[2], text[3], text[4], text[5], text[6], text[7], text[8])
            logging.debug(text[8])
            logging.debug("Rubric received")
            
            self.rubric_exists = self.yardstickDB.rubric_exists(rubric.rubric_sha, rubric.description)
            if self.rubric_exists == None:
                logging.debug("Update Status->Rubric: rubric_exists = None")
                self.yardstickDB.insert_rubric(rubric)
                rubric_id = self.yardstickDB.query_maxrubric()
                rubric = self.yardstickDB.query_rubric(rubric_id)
                RUBRICLIST.append(rubric)
                RUBRICTITLE.append(rubric.title)
                self.is_exists = False
                
                logging.debug("Update Status->Rubric: rubric_exists =None; is_exists = False")  
            else:
                logging.debug("Update Status->Rubric: rubric_exists = not None")
                self.is_exists = True
                logging.debug("Update Status->Rubric: is_exists = True")
                warning = gtk.MessageDialog(parent = None,buttons = gtk.BUTTONS_YES_NO, \
                                    flags =gtk.DIALOG_DESTROY_WITH_PARENT,\
                                    type = gtk.MESSAGE_WARNING,\
                                    message_format = "Rubric exists. Would like to overwrite?")
                result = warning.run()
                if(result == gtk.RESPONSE_YES):
                    logging.debug("Update Status->Rubric: response yes")
                    self.overwrite = True
                    warning.destroy()
                    self.yardstickDB.delete_rubric(self.rubric_exists)
                    self.yardstickDB.insert_rubric(rubric)
                elif(result == gtk.RESPONSE_NO):
                    logging.debug("Update Status->Rubric: response no")
                    warning.destroy()
                    self.overwrite = False
                warning.destroy()
            self.processpanel.destroy()
            self.load_window()
                
        if model_name == "Category":
            if self.is_exists == False or self.overwrite == True:
                logging.debug("Update Status->Category: is_exists = False")
                rubric_id = self.yardstickDB.query_maxrubric()
                category = Category(None, text[2], rubric_id, text[4],text[5])
                self.yardstickDB.insert_category(category)
                logging.debug("Update Status->Category: is_exists = False; category_inserted")

        if model_name == "Level":
            if self.is_exists == False or self.overwrite == True:
                logging.debug("Update Status->Level: is_exists = False")
                rubric_id = self.yardstickDB.query_maxrubric()
                category_id = self.yardstickDB.query_maxcategory()
                level = Level(None, text[2], text[3], category_id, rubric_id, text[6], text[7])
                self.yardstickDB.insert_level(level)
                logging.debug("Update Status->Level: level inserted")
        
    def _alert(self, title, text=None):
        alert = NotifyAlert(timeout=3)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()

    def _alert_cancel_cb(self, alert, response_id):
        self.remove_alert(alert)
        
    def _shared_cb(self, sender):
        self._setup()
        self.is_shared = True
        self._alert('Shared', 'The activity is shared')

    def _setup(self):
        self.text_channel = TextChannelWrapper(
            self.shared_activity.telepathy_text_chan,
            self.shared_activity.telepathy_conn)
        self.text_channel.set_received_callback(self._received_cb)
        self._alert("Activity Shared", "Connected")
        self.shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self.shared_activity.connect('buddy-left', self._buddy_left_cb)

    def _joined_cb(self, sender):
        if not self.shared_activity:
            return
        for buddy in self.shared_activity.get_joined_buddies():
            self._buddy_already_exists(buddy)
        self.is_shared = True
        self._setup()
        self._alert("Joined", "Joined Scorepad Activity")

    def _received_cb(self, buddy, text):
        if buddy:
            if type(buddy) is dict:
                nick = buddy['nick']
            else:
                nick = buddy.props.nick
        else:
            nick = '???'
        self.update_status(str(nick),text)

    def _buddy_joined_cb(self, sender, buddy):
        if buddy == self.owner:
            return
        self._alert(str(buddy.props.nick), "joined the activity")

    def _buddy_left_cb(self, sender, buddy):
        if buddy == self.owner:
            return
        self._alert(str(buddy.props.nick), "left")

    def _buddy_already_exists(self, buddy):
        if buddy == self.owner:
            return
        self._alert(str(buddy.props.nick), "is here")

    def sendbundle_cb(self, bundle):
        text = bundle
        if text:
            if self.text_channel:
                self.text_channel.send(text)
            else:
                print "Not connected"
        self._alert("Bundle", "sent!")
    
#    def main(self):
#        gtk.main()

class TextChannelWrapper(object):

    def __init__(self, text_chan, conn):
        self._activity_cb = None
        self._text_chan = text_chan
        self._conn = conn
        self._signal_matches = []

    def send(self, text):
        if self._text_chan is not None:
            self._text_chan[CHANNEL_TYPE_TEXT].Send(
                CHANNEL_TEXT_MESSAGE_TYPE_NORMAL, text)

    def set_received_callback(self, callback):
        if self._text_chan is None:
            return
        self._activity_cb = callback
        m = self._text_chan[CHANNEL_TYPE_TEXT].connect_to_signal('Received',
            self._received_cb)
        self._signal_matches.append(m)

    def _received_cb(self, identity, timestamp, sender, type_, flags, text):
        if self._activity_cb:
            try:
                self._text_chan[CHANNEL_INTERFACE_GROUP]
            except Exception:
                nick = self._conn[
                    CONN_INTERFACE_ALIASING].RequestAliases([sender])[0]
                buddy = {'nick': nick, 'color': '#000000,#808080'}
            else:
                buddy = self._get_buddy(sender)
            self._activity_cb(buddy, text)
            self._text_chan[
                CHANNEL_TYPE_TEXT].AcknowledgePendingMessages([identity])
        else:
            print "Disconnected"

    def _get_buddy(self, cs_handle):
        pservice = presenceservice.get_instance()
        tp_name, tp_path = pservice.get_preferred_connection()
        conn = Connection(tp_name, tp_path)
        group = self._text_chan[CHANNEL_INTERFACE_GROUP]
        my_csh = group.GetSelfHandle()
        if my_csh == cs_handle:
            handle = conn.GetSelfHandle()
        elif group.GetGroupFlags() & \
            CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES:
            handle = group.GetHandleOwners([cs_handle])[0]
        else:
            handle = cs_handle
            assert handle != 0

        return pservice.get_buddy_by_telepathy_handle(
            tp_name, tp_path, handle)
