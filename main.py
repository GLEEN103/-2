import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup

URL = "https://namu.wiki/w/%EB%9F%AC%EB%B8%8C%20%EB%9D%BC%EC%9D%B4%EB%B8%8C!/%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/%EC%97%90%ED%94%BC%EC%86%8C%EB%93%9C%20%EA%B0%80%EC%9D%B4%EB%93%9C#toc"

class Pointer:
    def __init__(self):
        self.path = list()

    def set_path(self, level, name):
        result = list()
        for i in range(level-1):
            if i == level-2:
                result.append(name)
            else:
                result.append(self.path[i])
        self.path = result

    def add_data_to_path(self, value):
        path = ""
        for i in self.path:
            path += "[\"" + str(i) + "\"]"

        temp = dict()
        if "스토리의 핵심인 뮤즈의 존속" in value['내용']:
            pass
        try:
            exec("""temp = result{0}""".format(path))
            exec("""result{0}["text"] += " " + "{1}" """.format(path, value['text']))
        except:
            exec("result{0} = {1}".format(path, value))

def header_name(text):
    text = text.split("[편집]")[0]
    text = text.split(" ")[1:]

    result = ""
    for i in text:
        result += " " + i

    return result[1:]

def find_text(element):
    result = ""
    for i in element.contents:
        for j in i.contents:
            if type(j).__name__ == "NavigableString": # 문자열일 경우
                result += " " + j
            else:
                try:
                    if j.attrs['class'] == ['Tx+lh99R']: # 주석일 경우
                        p = re.compile('#fn-\d+')
                        if p.fullmatch(j.attrs['href']):

                            annotate_text = ""
                            for k in annotate[int(j.attrs['href'].split("-")[1])-1].contents:
                                if type(k).__name__ == "NavigableString":
                                    annotate_text += " " + k
                            
                            annotate_text = " (" + annotate_text[1:] + ")"
                            result += annotate_text
                except:
                    pass
    
    return result



if __name__ == "__main__":

    driver = webdriver.Chrome()
    driver.get(URL)
    driver.implicitly_wait(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    global annotate
    annotate = soup.find_all('span', attrs={"class":"IDxMND79"}) # - 주석
    main_soup = soup.find('div', attrs={"class":"OZGMPIW5"}) # - 본문
    
    test = main_soup.find('h2')

    start_main = False
    global result
    result = dict()
    pointer = Pointer()
    p = re.compile('h\d')

    for value in main_soup.contents:

        # 본문에 진입했는지 검사
        if start_main == False:
            if value.name == 'h2':
                start_main = True
            else:
                continue

        try:
            if value.attrs['data-v-41f37ffa'] == '': # 광고 만나면 루프 종료
                break
        except:
            pass

        if p.fullmatch(value.name):
            if header_name(value.text) == "개요": # 개요 예외처리
                continue

            level = int(value.name[1:])
            pointer.set_path(level, header_name(value.text))
            
        elif value.name == 'div':
            pointer.add_data_to_path({"내용":find_text(value)}) 

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)