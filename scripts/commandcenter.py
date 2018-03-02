#!/usr/bin/env python3

from functools import partial
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory
import re
import json
import sys
import time
from collections import OrderedDict
from jinja2 import Template
import requests
# Copy to local
from .texttable import Texttable
from larva.client import LarvaProxy
from larva.config import Config


def split_token(cmd):
    WORD_RE = re.compile(r'([a-zA-Z0-9_,./:!]+)')
    result = list()
    item = re.finditer(WORD_RE, cmd)
    for i, m in enumerate(item):
        result.append(m.group())
    return result


manager = KeyBindingManager.for_prompt()


@manager.registry.add_binding('?')
def _(event):
    def print_hello():
        t = split_token(event.cli.buffers['DEFAULT_BUFFER'].text)
        result = list()
        if len(t) == 1:
            try:
                if t[0] in doc:
                    print('=' * 80)
                    for func in doc[t[0]]:
                        print(func, doc[t[0]][func]['description'])
            except:
                pass
        elif len(t) >= 2:
            try:
                table1 = Texttable()
                table1.set_deco(Texttable.VLINES | Texttable.HLINES | Texttable.BORDER | Texttable.HEADER)
                table1.set_chars(['', '|', ' ', '='])
                table1.set_cols_width([76])
                table1.add_rows([
                    ["{} {}".format(t[0], t[1])],
                    [doc[t[0]][t[1]]['description']]]
                )
                print(table1.draw())

                if 'Args' in doc[t[0]][t[1]]:
                    print("Args:")
                    result.append([ "Field", "Type", "Default", "Description"])

                    for func_args in doc[t[0]][t[1]]['Args']:
                        args_type = doc[t[0]][t[1]]['Args'][func_args]['type']
                        args_desc = doc[t[0]][t[1]]['Args'][func_args]['description']
                        if 'default' in doc[t[0]][t[1]]['Args'][func_args]:
                            args_default = doc[t[0]][t[1]]['Args'][func_args]['default']
                            result.append([func_args, args_type, args_default, args_desc])
                        else:
                            result.append([func_args, args_type, " ", args_desc])
                    table2 = Texttable()
                    table2.set_cols_align(["c", "c", "c", "c"])
                    table2.set_deco(Texttable.VLINES  | Texttable.BORDER| Texttable.HEADER)
                    table2.set_chars([' ', '|', ' ', '-'])
                    table2.add_rows(result)
                    print(table2.draw()+"\n")

                if 'Raises' in doc[t[0]][t[1]]:
                    print("Raises:")
                    result = []
                    result.append([ "Field", "Type", "Description"])
                    for func_raises in doc[t[0]][t[1]]['Raises']:
                        raises_type = doc[t[0]][t[1]]['Raises'][func_raises]['type']
                        raises_desc = doc[t[0]][t[1]]['Raises'][func_raises]['description']
                        result.append([func_raises, raises_type, raises_desc])
                    table3 = Texttable()
                    table3.set_deco(Texttable.VLINES | Texttable.BORDER | Texttable.HEADER)
                    table3.set_chars([' ', '|', ' ', '-'])
                    table3.add_rows(result)
                    print(table3.draw()+"\n")

                if 'Examples' in doc[t[0]][t[1]]:
                    print("Examples:")
                    table4 = Texttable()
                    table4.set_cols_align(["l"])
                    table4.set_deco(Texttable.VLINES)
                    table4.set_chars([' ', ' ', ' ', '-'])
                    table4.set_chars([' ', '=', ' ', '-'])
                    table4.add_rows([[""],[ doc[t[0]][t[1]]['Examples']]])
                    print(table4.draw())

            except:
                pass

    event.cli.run_in_terminal(print_hello)

status_bar = ""
input_status = ""
arg_default = ""


def get_bottom_toolbar_tokens(cli):
    return [(Token.Toolbar, status_bar)]


style = style_from_dict({
    Token.Toolbar: '#ffffff bg:#333333',

})

r = None
while r is None:
    try:
        r = requests.post('http://localhost:8080/')
        doc = json.loads(r.text, object_pairs_hook=OrderedDict)
    except:
        time.sleep(1)

# Get admin session from db
token_db = Config("token_db")
shell = None
for token in token_db:
    if token_db[token] == "admin":
        shell = LarvaProxy("localhost", port=8080, token=token)
        break
if shell is None:
    print("python-promise is not ready yet")
    sys.exit()


def parse_boolean(cmd):
    if cmd == "True":
        return True
    elif cmd == "False":
        return False
    else:
        raise ValidationError(message="value of %s is not a boolean" % cmd)


def parse_int(cmd):
    try:
        return int(cmd)
    except:
        raise ValidationError(message="value of %s is not an int" % cmd)


def parse_str(cmd):
    if cmd[0] == cmd[-1] == '"':
        return cmd[1:-1]
    else:
        return cmd


def parse_list(cmd):
    # Assume all str
    return cmd.split(',')


def parse_dict(cmd):
    try:
        result = json.loads(cmd)
        if not isinstance(result, dict):
            raise ValidationError(message="value of %s is not a dict" % cmd)
        return result
    except:
        raise ValidationError(message="value of %s is not a dict" % cmd)


type_convert_map = {"int": parse_int,
                    "str": parse_str,
                    "boolean": parse_boolean,
                    "list": parse_list,
                    "dict": parse_dict}


def parse_command(cmd):
    tokens = split_token(cmd)

    obj = doc[tokens[0]]
    method = obj[tokens[1]]

    parameter_list = tokens[2:]
    parameter_count = int(len(tokens[2:]) / 2)
    parameter_kwargs = dict()
    for i in range(0, parameter_count):
        key = parameter_list[i * 2]
        unformated_value = parameter_list[i * 2 + 1]
        value_type = method['Args'][key]['type']
        parameter_kwargs[key] = type_convert_map[value_type](unformated_value)

    if len(tokens[2:]) % 2 == 1 and len(tokens) > 2:
        parameter_kwargs[parameter_list[-1]] = None
    return tokens[0], tokens[1], parameter_kwargs


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        global status_bar
        global input_status
        global arg_default

        word = document.get_word_before_cursor()

        position = - len(word)

        tokens = split_token(document.text)

        token_position = len(tokens)
        if len(word) == 0:
            token_position += 1

        # Debug
        # status_bar = "[%s(%d), %d]:[%s] arg_default: %s ins:%s, comp:%s" % (
        #     str(tokens),
        #     token_position,
        #     position,
        #     word,
        #     arg_default,
        #     str(complete_event.text_inserted),
        #     str(complete_event.completion_requested))

        # Match Object
        if token_position == 1:
            status_bar = ""
            for m in doc:
                if word == m[:len(word)]:
                    yield Completion(m, start_position=position)
        # Match Method
        elif token_position == 2 and tokens[0] in doc:
            status_bar = ""
            for method in doc[tokens[0]]:
                if word == method[:len(word)]:
                    yield Completion(method, start_position=position,
                                     display_meta=doc[tokens[0]][method]['description'])
        # Match Parameters
        elif token_position > 2 and tokens[0] in doc and tokens[1] in doc[tokens[0]] and 'Args' in doc[tokens[0]][
            tokens[1]]:
            kwargs = doc[tokens[0]][tokens[1]]['Args'].items()
            args = list(kwargs)
            # Match parameter name
            if token_position % 2 == 1 and (len(word) == 0 or (word[0] != ',' or tokens[-1][-1] != ',')):
                try:
                    arg = args[int((token_position - 3) / 2)]
                    status_bar = arg[1]['description'].strip() + ': ' + arg[1]['type']
                    if 'default' not in arg[1]:
                        yield Completion(text=arg[0], display=arg[0], start_position=position,
                                         display_meta=arg[1]['description'])
                    else:
                        if len(word) == 0:
                            yield Completion(text='', display='<enter>', start_position=position,
                                             display_meta=' Sumbit Command')
                        for arg in args:
                            if 'default' in arg[1] and word == arg[0][:len(word)] and arg[0] not in tokens:
                                yield Completion(text=arg[0], display=arg[0], start_position=position,
                                                 display_meta=arg[1]['description'])
                except:
                    pass
            # Match Parameter Value
            else:
                # arg: ('pool_name', {'description': ' Pool name', 'type': 'str', 'htmltype': 'text'})

                arg = None
                # For the case:
                # obj method para
                for entry in args:
                    if entry[0] == tokens[-1]:
                        arg = entry
                # For the case:
                # obj method para value
                if arg is None:
                    for entry in args:
                        if entry[0] == tokens[-2]:
                            arg = entry
                if arg is None:
                    return

                if 'enum' in arg[1]:
                    for entry in arg[1]['enum']:
                        if word == entry[:len(word)]:
                            yield Completion(text=entry, display=entry, start_position=position)
                elif 'func' in arg[1]:
                    func = arg[1]['func']
                    qobj, qmethod, qkwargs = parse_command(document.text)
                    parameter_kwargs = dict()

                    if len(func) > 2:
                        for k in func[2]:
                            template = Template(func[2][k])
                            value_string = template.render(input=qkwargs)
                            value_type = doc[func[0]][func[1]]['Args'][k]['type']
                            parameter_kwargs[k] = type_convert_map[value_type](value_string)

                    try:
                        result_list = getattr(getattr(shell, func[0]), func[1])(**parameter_kwargs)
                    except:
                        return

                    for k in result_list:
                        if isinstance(result_list, list):
                            value = k['name']
                        else:
                            value = k
                        if len(word) == 0:
                            yield Completion(text=value, display=value, start_position=position)
                        elif value not in parse_list(tokens[token_position - 1]):
                            if word[0] == ',':
                                yield Completion(text=',' + value, display=value, start_position=position)
                            elif word == value[:len(word)]:
                                yield Completion(text=value, display=value, start_position=position)


class TokenValidator(Validator):
    def validate(self, document):
        tokens = split_token(document.text)
        run_length = 0

        if document.text in ["logout", "exit"]:
            return

        if len(tokens) == 0:
            raise ValidationError(message="Empty line", cursor_position=run_length)

        type_convert_map = {"int": parse_int,
                            "str": parse_str,
                            "boolean": parse_boolean,
                            "list": parse_list,
                            "dict": parse_dict}

        if len(tokens) % 2 != 0:
            raise ValidationError(message="Missing parameter", cursor_position=len(document.text))

        if tokens[0] not in doc:
            raise ValidationError(message='No such class', cursor_position=run_length)
        run_length += len(tokens[0]) + 1
        obj = doc[tokens[0]]

        if tokens[1] not in doc[tokens[0]]:
            raise ValidationError(message='No such function', cursor_position=run_length)
        run_length += len(tokens[1]) + 1
        method = obj[tokens[1]]

        parameter_list = tokens[2:]
        parameter_count = int(len(tokens[2:]) / 2)
        parameter_kwargs = dict()
        for i in range(0, parameter_count):
            key = parameter_list[i * 2]
            unformated_value = parameter_list[i * 2 + 1]
            if key not in method['Args']:
                raise ValidationError(message="No such parameter %s" % key, cursor_position=run_length)

            if list(method['Args'])[i] != key and 'default' not in method['Args'][key]:
                raise ValidationError(message="Parameter %s was missing" % list(method['Args'])[i],
                                      cursor_position=run_length)
            run_length += len(key) + 1

            value_type = method['Args'][key]['type']
            try:
                parameter_kwargs[key] = type_convert_map[value_type](unformated_value)
            except ValidationError as e:
                e.cursor_position = run_length
                raise e
            run_length += len(unformated_value) + 1


def default_print(res):
    if res is None:
        return

    table = Texttable()

    table_list = list()
    if isinstance(res, dict) and len(res) != 0:
        k = list(res)[0]
        table.set_deco(Texttable.HEADER | Texttable.VLINES)

        # default obj.list view
        if isinstance(res[k], dict):
            header_type = ["t"]
            header = ["name"]
            for k in res[k]:
                header.append(k)
                header_type.append('a')
            table.set_cols_dtype(header_type)
            table_list.append(header)
            for k in res:
                row = [k]
                for vaule_name in header[1:]:
                    if k in res and vaule_name in res[k]:
                        if isinstance(res[k][vaule_name], bool):
                            row.append(str(res[k][vaule_name]))
                        else:
                            row.append(res[k][vaule_name])
                    else:
                        row.append('')
                table_list.append(row)
            table.add_rows(table_list)
            print(table.draw())
        # default obj.info view
        else:
            header_type = ["t", "a"]
            header = ["key", "value"]
            table.set_cols_dtype(header_type)
            table_list.append(header)
            for k in res:
                table_list.append([k, str(res[k])])
            table.add_rows(table_list)
            print(table.draw())
    elif isinstance(res, str) or isinstance(res, int):
        print(res)
    elif isinstance(res, list):
        # No result
        if len(res) == 0:
            return

        if len(res) == 1:
            table.set_deco(Texttable.VLINES | Texttable.HLINES | Texttable.BORDER)

        table.set_chars(['-', '|', '+', '-'])

        for entry in res:
            col = list()
            col.append(entry)
            table_list.append(col)

        table.add_rows(table_list)
        print(table.draw())


def run_comamnd(cmd):
    global status_bar
    status_bar = ''
    obj, method, parameter_kwargs = parse_command(cmd)
    try:
        res = getattr(getattr(shell, obj), method)(**parameter_kwargs)
    except Exception as e:
        print(e)
        try:
            template = Template(method[e.name + "Format"])
            exception_output = template.render(input=parameter_kwargs, exception=e.args[0])
            print(exception_output)
            return
        except:
            print(e.args)
            return

    if obj in doc and method in doc[obj] and 'ReturnsFormat' in doc[obj][method]:
        template = Template(doc[obj][method]['ReturnsFormat'])
        shell_output = template.render(input=parameter_kwargs, output=res)
        print(shell_output)
    else:
        default_print(res)


def main():
    history = InMemoryHistory()

    # Non-interactive mode
    if len(sys.argv) > 2 and sys.argv[1] == '-c':
        run_comamnd(" ".join(sys.argv[2:]))
        sys.exit()

    while True:
        try:
            cmdline = prompt('promise > ', validator=TokenValidator(), completer=MyCustomCompleter(),
                             get_bottom_toolbar_tokens=get_bottom_toolbar_tokens, style=style,
                             key_bindings_registry=manager.registry, history=history)
            if cmdline == "logout" or cmdline == "exit":
                sys.exit()
            run_comamnd(cmdline)
        except KeyboardInterrupt:
            pass
        except EOFError as e:
            sys.exit()
