from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import time
import configparser
import json
import sys

class InstaBot:

    # init

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome('./chromedriver.exe')
        self.base_url = 'https://www.instagram.com/'
        self.login()

    # login

    def login(self):
        print('авторизация')
        self.driver.get('{}accounts/login/'.format(self.base_url))
        time.sleep(1)
        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button').click()
        time.sleep(2)

    # parse followers

    def follow_user(self, username):
        print('парсинг подписок ' + username)
        self.driver.get('{}{}/'.format(self.base_url, username))
        followers_count = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text
        print('кол-во подписок пользователя ' + followers_count)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()

        # скроллинг всего списка пользователей группы

        print('скроллинг всего списка пользователей')
        time.sleep(1)

        followers = []
        while len(followers) < int(followers_count):
            followers = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/ul/div/li')
            self.driver.execute_script('arguments[0].scrollIntoView()', followers[len(followers)-1])
            time.sleep(1)
        print('подписок найдено ' + str(len(followers)-1))

        # подписка на пользователей

        #followers = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/ul/div/li')
        for el in followers:
            button = el.find_element_by_tag_name('button')
            if button.text != 'Подписаться':
                continue
            button.click()
            time.sleep(1)
            for user in el.find_elements_by_tag_name('a'):
                if user.text != '':
                    print('подписка на ' + user.text)
              
    def unfollow_user(self, username):
        print('парсинг подписок ' + username)
        self.driver.get('{}{}/'.format(self.base_url, username))
        followers_count = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text
        print('кол-во подписок пользователя ' + followers_count)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()

        # скроллинг всего списка пользователей группы

        print('скроллинг всего списка пользователей')
        time.sleep(1)

        followers = []
        while len(followers) < int(followers_count):
            followers = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/ul/div/li')
            self.driver.execute_script('arguments[0].scrollIntoView()', followers[len(followers)-1])
            time.sleep(1)
        print('подписок найдено ' + str(len(followers)-1))

        # подписка на пользователей

        #followers = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/ul/div/li')
        for el in followers:
            button = el.find_element_by_tag_name('button')
            if button.text == 'Подписаться':
                continue
            button.click()
            time.sleep(1)
            self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div[3]/button[1]').click()
            time.sleep(2)
            for user in el.find_elements_by_tag_name('a'):
                if user.text != '':
                    print('отписка на ' + user.text)

# main

if __name__ == '__main__':
    
    # check params

    cparser = configparser.ConfigParser()
    cparser.read('./config.ini')
    print('Проверка настроек')

    ret = False    
    while ret == False:
    
        username = cparser['AUTH']['USERNAME']
        password = cparser['AUTH']['PASSWORD']
            
        if username is None:
            print('Пользователь не задан(о)')
        elif password is None:
            print('Пароль не задан(о)')
        else:
            ret = True
        if ret == False:
            answer = input('Для повторного запуска нажмите клавишу... Для выхода нажните 0: ')
            if answer == '0':
                sys.exit(0)
    
    # initial

    ig_bot = InstaBot(username, password)

    # actions

    ret = False
    while ret == False:
        print('Выберите действие:' + chr(10) +
              '1 - Подписка' + chr(10) +
              '2 - Отписка' + chr(10) +
              '0 - Выход')
        answer = input()
        print(answer)
        if answer == '1':
            follow_name = input('Введите логин пользователя: ')
            ig_bot.follow_user(follow_name)
        elif answer == '2':
            follow_name = input('Введите логин пользователя: ')
            ig_bot.unfollow_user(follow_name)
        elif answer == '0':
            ret = True
        else:
            print('Вы ввели неверное значение')
    else:
        sys.exit(0)