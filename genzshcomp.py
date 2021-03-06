#!/usr/bin/env python
"""automatic generated to zsh completion function file"""
import re
import sys
from optparse import OptionParser
import subprocess

try:
    import argparse
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
except ImportError:
    argparse = None


__version__ = '0.5.2'
__author__ = 'Hideo Hattroi <hhatto.jp@gmail.com>'
__license__ = 'NewBSDLicense'

__all__ = ["main", "CompletionGenerator", "HelpParser"]

USAGE_DOCS = """\
usage: genzshcomp FILE
             or
       USER_SCRIPT --help | genzshcomp"""


class InvalidParserTypeError(Exception):

    """Base Class for invalid parser type exception."""


def get_parser_type(parser_obj):
    """return to 'argparse' or 'optparse'"""
    if not hasattr(parser_obj, '__module__'):
        raise InvalidParserTypeError("not have attribute to '__module__'."
                                     " object-type='%s'" % type(parser_obj))
    parser_type = parser_obj.__module__
    if not parser_type in ('optparse', 'argparse'):
        raise InvalidParserTypeError("Invalid paresr type."
                                     " type='%s'" % type(parser_type))
    return parser_type


def _escape_strings(strings):
    """escape to squarebracket and doublequote.

    >>> print(_escape_strings("hoge"))
    hoge
    >>> print(_escape_strings("[hoge"))
    \[hoge
    >>> print(_escape_strings("hoge]"))
    hoge\]
    >>> print(_escape_strings("[hoge]"))
    \[hoge\]
    >>> print(_escape_strings('[ho"ge]'))
    \[ho\"ge\]
    """
    target_chars = "[]\"`"
    ret = []
    for string in strings:
        if string in target_chars:
            string = '\\' + string
        ret.append(string)
    return "".join(ret)


class CompletionGenerator(object):

    """Generator of (Z|Ba)sh Completion Function"""

    def __init__(self, commandname=None, parser=None, parser_type=None,
                 output_format=None):
        self.commandname = commandname
        self.parser = parser
        if not parser_type:
            parser_type = get_parser_type(parser)
        self.parser_type = parser_type
        self.output_format = output_format if output_format else 'zsh'

    def _get_dircomp(self, opt):
        """judged to directories and files completion.

        :return: ':' or ''
        :rtype: str
        """
        # version
        if self.parser_type == 'optparse':
            if '--version' == opt:
                return ":"
        else:   # argparse
            if '-v' == opt or '--version' == opt:
                return ":"
        # help
        if '-h' == opt or '--help' == opt:
            return ":"
        # user define options
        if self.parser_type == 'optparse':  # TODO: now, only optparse module
            opt_obj = self.parser._short_opt.get(opt)
            if opt_obj and opt_obj.action in ('store_true', 'store_false'):
                return ""
            else:
                opt_obj = self.parser._long_opt.get(opt)
                if opt_obj and opt_obj.action in ('store_true', 'store_false'):
                    return ""
        return ""

    def _get_list_format(self):
        """return to string of list format."""
        if self.parser_type == 'optparse':
            actions = self.parser.option_list
        elif self.parser_type == 'argparse':
            actions = self.parser._actions
        ret = []
        for action in actions:
            if self.parser_type == 'optparse':
                opts = [i for i in action._long_opts]
                opts += [i for i in action._short_opts]
            elif self.parser_type == 'argparse':
                opts = action.option_strings
            for opt in opts:
                if action.help:
                    tmp = "%s:%s" % (opt, _escape_strings(action.help))
                else:
                    tmp = "%s" % (opt)
                ret.append(tmp)
        return "\n".join(ret)

    def _get_bash_format(self):
        """return to string of bash completion function format."""
        ret = []
        ret.append("#!bash\n#")
        ret.append("# this is bash completion function file for %s." %
                   self.commandname)
        ret.append("# generated by genzshcomp(ver: %s)\n#\n" % __version__)
        ret.append("_%s()\n{" % self.commandname)
        ret.append(
            "  local cur\n  local cmd\n\n  cur=${COMP_WORDS[$COMP_CWORD]}")
        ret.append("  cmd=( ${COMP_WORDS[@]} )\n")
        if self.parser_type == 'optparse':
            actions = self.parser.option_list
        elif self.parser_type == 'argparse':
            actions = self.parser._actions
        opts = []
        for action in actions:
            if self.parser_type == 'optparse':
                opts += [i for i in action._long_opts]
                opts += [i for i in action._short_opts]
            elif self.parser_type == 'argparse':
                opts += action.option_strings
        ret.append("  if [[ \"$cur\" == -* ]]; then")
        ret.append(
            "    COMPREPLY=( $( compgen -W \"%s\" -- $cur ) )" % " ".join(opts))
        ret.append("    return 0")
        ret.append("  fi")
        ret.append("}\n")
        ret.append("complete -F _%s -o default %s" %
                   (self.commandname, self.commandname))
        return "\n".join(ret)

    def _get_zsh_format(self):
        """return to string of zsh completion function format."""
        if self.parser_type == 'optparse':
            actions = self.parser.option_list
        elif self.parser_type == 'argparse':
            actions = self.parser._actions
        ret = []
        ret.append("#compdef %s" % self.commandname)
        ret.append("#\n# this is zsh completion function file.")
        ret.append("# generated by genzshcomp(ver: %s)\n#\n" % __version__)
        ret.append("typeset -A opt_args")
        ret.append("local context state line\n")
        ret.append("_arguments -s -S \\")
        for action in actions:
            if action.metavar:
                if self.parser_type == 'argparse' and \
                        action.metavar[0] == '{' and action.metavar[-1] == '}':
                    metas = action.metavar[1:-1].split(',')
                    metavar = "::%s:(%s):" % (action.metavar, " ".join(metas))
                else:
                    metavar = "::%s:_files" % action.metavar
            elif action.choices and self.parser_type == 'argparse':
                metavar = ":::(%s):" % (" ".join(action.choices))
            else:
                metavar = ""

            if self.parser_type == 'optparse':
                opts = [i for i in action._long_opts]
                opts += [i for i in action._short_opts]
            elif self.parser_type == 'argparse':
                opts = action.option_strings
            for opt in opts:
                directory_comp = self._get_dircomp(opt)
                if action.help:
                    tmp = "  \"%s[%s]%s%s\" \\" % (opt,
                                                   _escape_strings(
                                                       action.help),
                                                   metavar, directory_comp)
                else:
                    tmp = "  \"%s%s%s\" \\" % (opt, metavar, directory_comp)
                ret.append(tmp)
        ret.append("  \"*:args:_files\"")
        return "\n".join(ret)

    def get(self):
        """_get_X_format wrapper method"""
        func = getattr(self, "_get_%s_format" % self.output_format)
        return func()


class HelpParser(object):

    """convert from help-strings to optparse.OptionParser"""

    def __init__(self, helpstrings):
        self.helplines = helpstrings.splitlines()
        for cnt, line in enumerate(self.helplines):
            if re.match("Options:", line):
                self.parselines = self.helplines[cnt:]
                self.parser_type = 'optparse'
                return
            elif re.match("optional arguments:", line):
                self.parselines = self.helplines[cnt:]
                self.parser_type = 'argparse'
                return
        raise InvalidParserTypeError("Invalid paresr type.")

    def get_commandname(self):
        """get command name from help strings."""
        for line in self.helplines:
            if "Usage:" in line and self.parser_type is 'optparse':
                tmp = line.split()
                return tmp[1]
            if "usage:" in line and self.parser_type is 'argparse':
                tmp = line.split()
                return tmp[1]
        return None

    def _get_helpoffset(self):
        """get offset-position of help-strings.

        :param line: line
        :param line: str
        :return: offset position
        :rtype: int
        """
        return re.search("show ", self.parselines[1]).start()

    def _get_parserobj(self, option_list):
        """judged to parser type, return tp parser object

        :param option_list: parser option list
        :return: parser object, optparse.OptionParser or
                 argparse.ArgumentParser
        :rtype: parser object class
        """
        if '--version' in self.parselines[0]:
            if argparse and 'argparse' == self.parser_type:
                parser = ArgumentParser(version='dummy',
                                        formatter_class=RawDescriptionHelpFormatter)
            else:
                parser = OptionParser(version="dummy")
        else:
            if argparse and 'argparse' == self.parser_type:
                parser = ArgumentParser(
                    formatter_class=RawDescriptionHelpFormatter)
            else:
                parser = OptionParser()
        for opt in option_list:
            if opt['short'] and self.parser_type is 'optparse':
                if parser.has_option(opt['short']):
                    parser.remove_option(opt['short'])
                parser.add_option(opt['short'], opt['long'],
                                  metavar=opt['metavar'],
                                  help=opt['help'].strip())
            elif not opt['short'] and self.parser_type is 'optparse':
                if parser.has_option(opt['short']):
                    parser.remove_option(opt['short'])
                parser.add_option(opt['long'],
                                  metavar=opt['metavar'],
                                  help=opt['help'].strip())
            elif opt['long'] and opt['short'] and \
                    self.parser_type is 'argparse':
                if opt['metavar'] is None:
                    parser.add_argument(opt['short'], opt['long'],
                                        action='store_true',
                                        help=opt['help'].strip())
                else:
                    parser.add_argument(opt['short'], opt['long'],
                                        metavar=opt['metavar'],
                                        help=opt['help'].strip())
            elif opt['short'] and self.parser_type is 'argparse':
                if opt['metavar'] is None:
                    parser.add_argument(opt['short'],
                                        action='store_true',
                                        help=opt['help'].strip())
                else:
                    parser.add_argument(opt['short'],
                                        metavar=opt['metavar'],
                                        help=opt['help'].strip())
            elif not opt['short'] and self.parser_type is 'argparse':
                if opt['metavar'] is None:
                    parser.add_argument(opt['long'],
                                        action='store_true',
                                        help=opt['help'].strip())
                else:
                    parser.add_argument(opt['long'],
                                        metavar=opt['metavar'],
                                        help=opt['help'].strip())
            else:
                raise InvalidParserTypeError("Invalid paresr type.")
        return parser

    def help2parseobj(self):
        """wrapper of help2optparse and help2argparse."""
        if self.parser_type == 'optparse':
            _method = self.help2optparse
        else:
            _method = self.help2argparse
        return _method()

    def help2optparse(self):
        """convert from help strings to optparse.OptionParser object."""
        helpstring_offset = self._get_helpoffset()
        option_cnt = -1
        option_list = []
        # 1 is 'Options' line
        for line in self.parselines[1:]:
            if line.isspace() or not len(line) or '--help     ' in line:
                continue
            tmp = line.split()
            metavar = None
            if line.find('--') < helpstring_offset and tmp[0][:2] == '--':
                # only long option
                longopt = tmp[0]
                longopt_length = 0
                if '=' in longopt:
                    longtmp = longopt.split("=")
                    longopt = longtmp[0]
                    metavar = longtmp[1]
                    longopt_length += len(metavar) + 1
                longopt_length += len(longopt) + line.find('--')
                # check to exist help strings
                if longopt_length > helpstring_offset:
                    helpstrings = ""
                else:
                    helpstrings = line[helpstring_offset:] + ' '
                option_list.append({'short': None,
                                    'long': longopt,
                                    'metavar': metavar,
                                    'help': helpstrings})
                option_cnt += 1
            elif line.find('--') < helpstring_offset and tmp[0][0] == '-':
                # short option
                shortopt = line.split(', ')[0].lstrip().split()[0]
                longopt = None
                if len(line) < helpstring_offset:
                    help_string = ""
                elif line[helpstring_offset - 1] is ' ':
                    help_string = line[helpstring_offset:]
                else:
                    help_string = ""
                # check exist longopt
                if line.find(', --') != -1:     # exist long option
                    tmp = line.split(', ')
                    if tmp[1][:2] == '--':
                        longopt = tmp[1]
                        if '=' in longopt:
                            longtmp = longopt.split("=")
                            longopt = longtmp[0]
                            metavar = longtmp[1]
                        else:
                            longopt = tmp[1].split()[0]
                    else:   # found metavar
                        metavar = tmp[1][:-1]
                        longopt = tmp[2].split("=")[0]
                else:                           # not exist long option
                    tmp = line.split()
                    shortopt = tmp[0]
                    metavar = tmp[1]
                    if len(tmp) > 2:
                        help_string += line[helpstring_offset - 1]
                option_list.append({'short': shortopt,
                                    'long': longopt,
                                    'metavar': metavar,
                                    'help': help_string + ' '})
                option_cnt += 1
            else:
                # only help-strings line
                option_list[option_cnt]['help'] += line[helpstring_offset:]
                option_list[option_cnt]['help'] += " "
        return self._get_parserobj(option_list)

    def help2argparse(self):
        """convert from help strings to argparse.ArgumentParser object."""
        helpstring_offset = self._get_helpoffset()
        option_cnt = -1
        option_list = []
        for line in self.parselines[1:]:
            if line.isspace() or not len(line) or '--help     ' in line or \
               '--version  ' in line:
                continue
            tmp = line.split()
            metavar = None
            if (2 <= helpstring_offset or line[2] == '-') and \
                    len(tmp) > 2 and tmp[2][0] == '-':
                # (long option and) short option and exist METAVAR
                if tmp[0][0] != '-':
                    # invalid
                    option_list[option_cnt]['help'] += line[helpstring_offset:]
                    option_list[option_cnt]['help'] += " "
                    continue
                optlist = line.split()
                longopt = optlist[0]
                shortopt = optlist[2]
                metavar = optlist[1][:-1]
                if len(line) >= helpstring_offset and line[helpstring_offset - 1] is ' ':
                    help_string = line[helpstring_offset:]
                else:
                    help_string = ""
                option_list.append({'short': shortopt,
                                    'long': longopt,
                                    'metavar': metavar,
                                    'help': help_string + ' '})
                option_cnt += 1
            elif line.find('--') < helpstring_offset and len(tmp) > 1 and \
                    tmp[1][0] == '-':
                # (long option and) short option and not exist metavar
                optlist = line.split()
                longopt = optlist[0][:-1]
                shortopt = optlist[1]
                if len(line) >= helpstring_offset and line[helpstring_offset - 1] is ' ':
                    help_string = line[helpstring_offset:]
                else:
                    help_string = ""
                option_list.append({'short': shortopt, 'long': longopt,
                                    'metavar': None, 'help': help_string + ' '})
                option_cnt += 1
            elif line.find('--') < helpstring_offset and tmp[0][:2] == '--':
                # only long option
                longopt = tmp[0]
                longopt_offset = len(longopt) + 2
                metavar = None
                # check exist METAVAR
                if longopt_offset == len(line):
                    # only option value
                    pass
                elif line[longopt_offset] == ' ' and \
                        re.search('[a-zA-Z[{]', line[longopt_offset + 1]):
                    metavar = tmp[1]
                    longopt_offset += len(metavar) + 1
                # check to exist help strings
                if longopt_offset > helpstring_offset:
                    helpstrings = ""
                else:
                    helpstrings = line[helpstring_offset:] + ' '
                option_list.append({'short': None,
                                    'long': longopt,
                                    'metavar': metavar,
                                    'help': helpstrings})
                option_cnt += 1
            else:
                # only help-strings line
                option_list[option_cnt]['help'] += line[helpstring_offset:]
                option_list[option_cnt]['help'] += " "
        return self._get_parserobj(option_list)


def main():
    """tool main"""
    oparser = ArgumentParser(version=__version__,
                           description=__doc__,
                           usage=USAGE_DOCS)
    oparser.add_argument("-f", "--output-format", dest="output_format",
                       help="output format type [zsh|bash|list] (default: zsh)")
    oparser.add_argument("-n", "--command-name", help='override command name')

    help_text_group = oparser.add_mutually_exclusive_group()
    help_text_group.add_argument('-c', '--command', help='command to execute to get --help')
    help_text_group.add_argument('-t', '--help-text', dest='help_text_file',
                                 help='file with output of --help')
    args = oparser.parse_args()
    if args.command is not None:
        cmd = args.command.strip()
        if not (cmd.endswith(' --help') or cmd.endswith(' -h')):
            cmd += ' --help'
        helptext = subprocess.check_output(cmd, shell=True)
    elif args.help_text_file is not None:
        helptext = open(args.help_text_file).read()
    elif sys.stdin.isatty():
        oparser.print_help()
        return -1
    else:
        helptext = sys.stdin.read()
    help_parser = HelpParser(helptext)
    command_name = (args.command_name if args.command_name is not None else
                    help_parser.get_commandname())
    option_parser = help_parser.help2parseobj()
    compobj = CompletionGenerator(command_name, option_parser,
                                  output_format=args.output_format)
    print(compobj.get())
    return 0


if __name__ == '__main__':
    sys.exit(main())
