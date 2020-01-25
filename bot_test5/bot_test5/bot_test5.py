from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import time
import configparser
import json
import sys

class VkBot:

    # инициализация класса

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome('./chromedriver.exe')
        self.base_url = 'https://vk.com/'
        #self.group_followers = []
        self.login()

    # вход вк

    def login(self):
        self.driver.get('{}/login/'.format(self.base_url))
        self.driver.find_element_by_xpath('//*[@id="email"]').send_keys(self.username)
        self.driver.find_element_by_xpath('//*[@id="pass"]').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="login_button"]').click()
        time.sleep(2)

    # парсинг сообщества

    def parse_community(self, community_name):
        print('парсинг сообщества ' + community_name)
        self.driver.get('{}/{}'.format(self.base_url, community_name))
        time.sleep(0.5)

        # определение группа или паблик

        try:
            self.driver.find_element_by_xpath('//*[@id="group_followers"]/a/div/span[1]').click()
            print('сообщество = группа')
        except Exception as E:
            try:
                self.driver.find_element_by_xpath('//*[@id="public_followers"]/a/div/span[1]').click()
                print('сообщество = паблик')
            except Exception as E:
                print('ошибка: не удается найти список пользователей сообщества')

        # скроллинг всего списка пользователей группы

        print('скроллинг всего списка пользователей')
        time.sleep(0.5)
        scroll_box = self.driver.find_element_by_xpath('//*[@id="box_layer"]/div[2]')
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            time.sleep(0.5)
            scroll_box.send_keys(Keys.END)
            ht = scroll_box.size['height']
            #print(str(ht))

        # парсинг всех пользователей

        print('парсинг пользователей')
        followers = self.driver.find_elements_by_css_selector('.fans_fan_lnk')
        followers_list = []
        for follower in followers:
            if follower:
                followers_list+=[follower.get_attribute('href')]
        print('кол-во пользователей ' + str(len(followers_list)))
        json_string = json.dumps({'response':followers_list})
        json_file = open(community_name + '.json', 'w+')
        json_file.write(json_string)
        json_file.close()

    # получение списка пользователей сообщества из файла

    def get_json_followers(self, file_name):
        print('получение списка пользователей сообщества из файла ' + file_name)
        community_followers = []
        if os.path.exists(file_name + '.json'):
            json_file = open(file_name + '.json', 'r')
            if json_file.mode == 'r':
                json_string = json_file.read()
                json_object = json.loads(json_string)
                for el in json_object['response']:
                    if el:
                        community_followers += [el]
                print('кол-во пользователей ' + str(len(community_followers)))
            json_file.close()
        return community_followers

    # отправка сообщения пользователям сообщества

    def send_messages(self, community_name, message, messages_count):
        print('отправка сообщения пользователям сообщества ' + community_name)

        # поиск пользователей которым отправили сообщение
        
        print('поиск пользователей которым отправили сообщение')
        send_followers = []
        if os.path.exists(community_name + '_send.json'):
            json_file = open(community_name + '_send.json', 'r')
            if json_file.mode == 'r':
                json_string = json_file.read()
                json_object = json.loads(json_string)
                for el in json_object['response']:
                    if el:
                        send_followers += [el]
                print('кол-во пользоватей ' + str(len(send_followers)))
            json_file.close()

        # поиск пользователей которым надо отправить сообщение

        print('поиск пользователей которым надо отправить сообщение')
        community_followers = self.get_json_followers(community_name)
        if len(community_followers) == 0:
            print('кол-во пользователей ' + str(len(community_followers)));
            return
        elif len(send_followers) == len(community_followers):
            print('сообщения уже всем отправлены')
            return

        # отправка сообщений + запись получателей

        print('отправка сообщений')
        i = 0
        for user in community_followers:
            if user and i < int(messages_count) and user not in send_followers:
                try:
                    #self.driver.get('{}/{}'.format(self.base_url, user))
                    self.driver.get(user)
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="profile_message_send"]/div/a[1]/button').click()
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="mail_box_editable"]').send_keys(message)
                    self.driver.find_element_by_xpath('//*[@id="mail_box_send"]').click()
                    i += 1
                    print('отправлено пользователю ' + user)
                except Exception as E:
                    print('не отправить пользователю ' + user)
                send_followers += [user]

        # запись получателей

        print('запись получателей')
        if i > 0:
            json_string = json.dumps({'response':send_followers})
            json_file = open(community_name + '_send.json', 'w+')
            json_file.write(json_string)
            json_file.close()

# main

if __name__ == '__main__':
    
    # проверка кофига

    cparser = configparser.ConfigParser()
    cparser.read('./config.ini')
    print('Проверка настроек')

    ret = False    
    while ret == False:
    
        username = cparser['AUTH']['USERNAME']
        password = cparser['AUTH']['PASSWORD']
        messages_count = cparser['COUNT']['MESSAGES']
        message = None
        if os.path.exists('message.txt'):
            msg_file = open('message.txt', 'r')
            if msg_file.mode == 'r':
                message = msg_file.read()
            msg_file.close()
            
        if username is None:
            print('Пользователь не задан(о)')
        elif password is None:
            print('Пароль не задан(о)')
        elif messages_count is None:
            print('Кол-во сообщений не задан(о)')
        elif message is None:
            print('Сообщение не задан(о)')
        else:
            ret = True
        if ret == False:
            answer = input('Для повторного запуска нажмите клавишу... Для выхода нажните 0: ')
            if answer == '0':
                sys.exit(0)
    
    # предварительный логин вк

    vk_bot = VkBot(username, password)

    # выбор действий программы

    ret = False
    while ret == False:
        print('Выберите действие:' + chr(10) +
              '1 - Отправка сообщений(далее будет доступен выбор сообщества)' + chr(10) +
              '2 - Парсинг сообщества(если вы еще не парсили либо надо обновить)' + chr(10) +
              '0 - Выход')
        answer = input()
        print(answer)
        if answer == '1':
            community_name = input('Введите название сообщества: ')
            vk_bot.send_messages(community_name, message, messages_count)
        elif answer == '2':
            community_name = input('Введите название сообщества: ')
            vk_bot.parse_community(community_name)
        elif answer == '0':
            ret = True
        else:
            print('Вы ввели неверное значение')
    else:
        sys.exit(0)