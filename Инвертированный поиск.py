import re
import pandas


#--- stemmer Porter ---
RVRE = re.compile(r'^(.*?[аеиоуыэюя])(.*)$')
PERFECTIVEGROUND = re.compile(r'((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$')
REFLEXIVE = re.compile(r'(с[яь])$')
ADJECTIVE = re.compile(r'(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$')
VERB = re.compile(r'((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить'
                  r'|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$')
NOUN = re.compile(r'(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию'
                  r'|ью|ю|ия|ья|я)$')
I = re.compile(r'и$')
PARTICIPLE = re.compile(r'((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$')
DERIVATIONAL = re.compile(r'(ость|ост)$')
P = re.compile(r'ь$')
NN = re.compile(r'нн$')
SUPERLATIVE = re.compile(r'(ейше|ейш)$')
NOT_LETTER = re.compile(r'[^a-яА-Яё]$')


#--- stop-symbols ---
NEWLINE_SYMBOLS = re.compile(r'-\n|\n|\t')
STOP_SYMBOLS = re.compile(r'\s(-|а|без|более|больше|будет|будто|бы|был|была|были|было|быть|в|вам|вас|вдруг|ведь|во'
                          r'|вот|впрочем|все|всегда|всего|всех|всю|вы|г|где|говорил|да|даже|два|для|до|еще|ж|же|жизнь'
                          r'|за|зачем|здесь|и|из|из-за|или|им|иногда|их|к|кажется|как|какая|какой|когда|конечно|которого'
                          r'|которые|кто|куда|ли|лучше|между|меня|мне|много|может|можно|мой|моя|него|нее|ней|нельзя|нет'
                          r'|ни|нибудь|никогда|ним|них|ничего|но|ну|о|об|один|он|она|они|опять|от|перед|по|под|после|потом'
                          r'|потому|почти|при|про|раз|разве|с|сам|свое|сказать|со|совсем|так|такой|там|тебя|тем|теперь'
                          r'|то|тогда|того|тоже|только|том|тот|три|тут|ты|у|уж|уже|хорошо|хоть|чего|человек|чем|через'
                          r'|что|чтоб|чтобы|чуть|эти|этого|этой|другой|его|ее|ей|ему|если|есть|мы|на|над|надо|наконец'
                          r'|нас|не|свою|себе|себя|сегодня|сейчас|сказал|сказала|этом|этот|эту|я)\s')
OTHER_SYMBOLS = re.compile(r'\.|\'|\"|!|\?|,|:|&|\*|@|#|№|\(|\)|\[|\]|\{|\}|\$|%|\^|\\|/|;|\<|\>|\+|\-|\=|\s\d+|\d+\s')

# --- variables ---
Documents = {}
DictWords = {}
counter_word = 0
path = "D:\\Учёба\\7 семестр (-)\\- Технологии обработки информации (Экз)\\Лабораторная работа №4\\"
Inverse = {}


# класс описывает, как будут храниться данные о файлах в словаре Documents
class DocumentRecord:
    def __init__(self, author, filename, filetype, path, array_filetext):
        self.author = author                            # автор. Всегда Дмитрий
        self.filename = filename.split('.')[0]          # имя файла
        self.filetype = filetype                        # тип файла
        self.path = path                                # путь к файлу
        self.array_filetext = array_filetext            # текст в виде массива
        self.score = 0

    def __repr__(self):
        return self.filename


# функция запрашивает имена файлов и помещает необходимые данные в словарь Documents
def input_data():
    global counter_word
    print("Необходимо ввести имена файлов")
    i = 0
    while True:
        file_name = input("Укажите имя файла или введите 'END' для завершения ввода: ")
        if file_name.upper() == 'END':
            break
        print(path+file_name)
        text_file = get_text(file_name)
        if text_file[0] != '' and text_file[0] != False:
            Documents[i] = DocumentRecord("Дмитрий", text_file[1], "TXT", path + file_name, delete_stop_symbols(text_file[0]).strip().split(' '))  # создали первую таблицу
            array_words = Documents[i].array_filetext                                     # список слов НЕ ОБРАБОТАННЫХ
            for index in range(len(array_words)):                                         # список слов ОБРАБОТАННЫХ
                array_words[index] = stemming(array_words[index]).lower()
            for word in array_words:                                                      # создали вторую таблицу
                if word in DictWords:
                    continue
                else:
                    DictWords[word] = counter_word
                    counter_word += 1
            for word in array_words:                                                      # создали третью таблицу
                DocId = DictWords[word]
                if DocId in Inverse:
                    Inverse[DocId].add(i)
                else:
                    Inverse[DocId] = {i}
            i += 1
        elif text_file[0] == '':
            continue
        else:
            break


# функция обрабатывает текст. Подготоваливаем к операции Стемминга Портера. Она необходима для оптимизированного
# составления словаря
def delete_stop_symbols(text):
    text = text.lower()
    result = NEWLINE_SYMBOLS.sub('', text)
    result = OTHER_SYMBOLS.sub('', result)
    result = ' ' + result + ' '
    result = STOP_SYMBOLS.sub(' ', result)
    return result


# функция считывает тексты из файлов.
def get_text(file_name):
    path_to_file = path + file_name + ".txt"
    text = ''
    while True:
        try:
            file = open(path_to_file, "r")

            for line in file:
                text += line
            file.close()
            return [text, file_name]

        except:
            file_name = input("Не найден указанный файл. Попробуйте еще раз, или введите 'END', чтобы завершить: " + "\n")
            if file_name.upper() == "END":
                break
            else:
                path_to_file = path + file_name + ".txt"
                continue

    return [False]


# функция реализует алгоритм стемминга. Принимает слово, возвращает основу слова.
def stemming(word):
    word = word.lower()
    word = word.replace('ё', 'e')
    area = re.match(RVRE, word)

    if area is not None:
        PREFIX = area.group(1)
        RV = area.group(2)

        # step 1
        template = PERFECTIVEGROUND.sub('', RV, 1)
        if template == RV:
            RV = REFLEXIVE.sub('', RV, 1)
            template = ADJECTIVE.sub('', RV, 1)

            if template != RV:
                RV = template
                RV = PARTICIPLE.sub('', RV, 1)
            else:
                template = VERB.sub('', RV, 1)
                if template == RV:
                    RV = NOUN.sub('', RV, 1)
                else:
                    RV = template
        else:
            RV = template

        # step 2
        RV = I.sub('', RV, 1)

        # step 3
        RV = DERIVATIONAL.sub('', RV, 1)

        # step 4
        template = NN.sub('н', RV, 1)
        if template == RV:
            template = SUPERLATIVE.sub('', RV, 1)
            if template != RV:
                RV = template
                RV = NN.sub('н', RV, 1)
            else:
                RV = P.sub('', RV, 1)
        else:
            RV = template
        word = PREFIX + RV
    return word


# функция для расчета показателя релевантности - Score. Принимает первым аргументом - список слов из запроса, вторым
# аргументом - текст в виде массива
def get_score(search_request, array_filetext):
    Wsingle = 0                     # вхождение одного слова
    Wpair = 0                       # вхождение пары
    Wphrase = 0                     # вхождение запроса целиком
    Wallwords = 0                   # наличие все слов запроса в документе

    for i in range(len(array_filetext)):
        array_filetext[i] = stemming(array_filetext[i])

    # функции для получения W.
    def get_Wsingle(search_request, array_filetext, Wsingle):
        for word in array_filetext:
            if word in search_request:
                Wsingle += 1
        return Wsingle

    def get_Wpair(search_request, array_filetext, Wpair):
        for k in range(len(search_request) - 1):
            for i in range(len(array_filetext) - 1):
                if ' '.join(search_request[k : k + 2]) == ' '.join(array_filetext[i : i + 2]):
                    Wpair += 1
        return Wpair

    def get_Wphrase(search_request, array_filetext, Wphrase):
        for i in range(len(array_filetext) - len(search_request) + 2):
            if ' '.join(search_request) == ' '.join(array_filetext[i : i + len(search_request)]):
                Wphrase += 1
        return Wphrase

    def get_Wallwords(search_request, array_filetext, Wallwords):
        dict_frequency = {}
        for word in search_request:
            dict_frequency[word] = 0
            for el in array_filetext:
                if el == word:
                    dict_frequency[word] += 1
        Wallwords = dict_frequency[list(dict_frequency.keys())[0]]
        for key in dict_frequency:
            if Wallwords > dict_frequency[key]:
                Wallwords = dict_frequency[key]
        return Wallwords


    if len(search_request) == 1:
        Wsingle = get_Wsingle(search_request, array_filetext, Wsingle)
        return score_formule(Wsingle)

    if len(search_request) == 2:
        Wsingle = get_Wsingle(search_request, array_filetext, Wsingle)
        Wpair = get_Wpair(search_request, array_filetext, Wpair)
        return score_formule(Wsingle, Wpair)

    if len(search_request) > 2:
        Wsingle = get_Wsingle(search_request, array_filetext, Wsingle)
        print("W single = " + str(Wsingle))
        Wpair = get_Wpair(search_request, array_filetext, Wpair)
        print("W pair = " + str(Wpair))
        Wphrase = get_Wphrase(search_request, array_filetext, Wphrase)
        print("W phrase = " + str(Wphrase))
        Wallwords = get_Wallwords(search_request, array_filetext, Wallwords)
        print("W allwords = " + str(Wallwords))
        return score_formule(Wsingle, Wpair, Wphrase, Wallwords)


def score_formule(Wsingle = 0, Wpair = 0, Wphrase = 0, Wallwords = 0, k1 = 1, k2 = 1/350):
    return Wsingle + Wpair + Wphrase * k2 + Wallwords * k1


# поисковая строка
def search():
    search_line = []
    while True:
        request = input("Введите поисковый запрос или 'STOP', чтобы закончить: ").strip()
        if request.upper() == "STOP":
            break
        elif request == "":
            continue
        else:
            request = re.sub(r"\s+", " ", request)
            search_line = request.split(' ')
            result = Inverse[DictWords[stemming(search_line[0])]]
            for word in search_line:
                key = stemming(word)
                if key in DictWords:
                    _set = Inverse[DictWords[key]]
                    result = _set & result
            for i in range(len(search_line)):
                search_line[i] = stemming(search_line[i])
            print("Запрос: ")
            print(search_line)
            print("Документы, в которых присутствуют совпадения: ")
            for el in result:
                print(Documents[el].filename)
            break

    for doc in Documents:
        Documents[doc].score = get_score(search_line, Documents[doc].array_filetext)
        print('Документ ' + Documents[doc].filename + ' имеет значение релевантности Score: ' + str(Documents[doc].score))


def print_data(Documents):
    result = {}
    for obj in Documents:
        result[Documents[obj].score] = obj
    reverse_list = sorted(list(result.keys()), reverse=True)
    for el in reverse_list:
        print("Файл " + Documents[result[el]].filename + ". Score = " + str(el))



input_data()
print("-------------------- Словарь документов и IdDoc  -----------------------")
print(Documents)
print("-------------------- Словарь слова и IdWord -----------------------")
print(DictWords)
print("-------------------- Словаь IdWord и IdDoc-----------------------")
print(Inverse)
search()
print("Файлы, отсортированные по релевантности: ")
print_data(Documents)

