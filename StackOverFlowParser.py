from StringIO import StringIO
import sys


class TokenizationError(Exception):
    """
    Tokenization Error
    """
    pass


class ParserError(Exception):
    """
    Parsing Error
    """
    pass


class TokenIndexes(object):
    """
    attribute Indexes for token string
    """

    IDENTITY = 0
    HEADING_LEVEL = 1
    HEADING_CONTENT = 2
    PARAGRAPH_CONTENT = 1


class ListTypes(object):
    """
    Type of List Headers
    """

    OPTIONS = 6
    NUMBER, ALPHA, ROMAN, LOWALPHA, STAR, PLUS = range(OPTIONS)

    @staticmethod
    def convertRoman(num):
        """
        Class Method to convert a number to Roman string
        """
        conv = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'],
                [100, 'C'], [90, 'XC'], [50, 'L'], [40, 'XL'],
                [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'],
                [1, 'I']]
        roman = ""
        i = 0
        while num > 0:
            while conv[i][0] > num:
                i += 1
            roman += conv[i][1]
            num -= conv[i][0]
        return roman


class Node(object):
    """
    Generic Node

    @attributes
    Children - List of the node's children
    Parent - parent node of this node
    Content - conent of the node (name for document node)
    """

    def __init__(self, content=""):
        self.children = []
        self.parent = None
        self.content = content

    @property
    def position(self):
        """
        GET the position of this node among siblings
        """
        if self.parent:
            return self.parent.children.index(self)

    def addChild(self, node):
        """
        Add a child node to list of children
        """
        self.children.append(node)

    def addParent(self, node):
        """
        Add parent node to current node
        """
        self.parent = node

    def expandContent(self, content):
        """
        Append additional content to current node's content
        """
        self.content += content

    def __repr__(self):
        return self.content


class Heading(Node):
    """
    Heading Node (Child of Node class)

    @attributes
    Base attributes
    +
    level - level of the heading node
    """

    def __init__(self, level, content):
        super(Heading, self).__init__(content)
        self.level = level

    @property
    def outline_prefix(self):
        """
        GET the listing prefix(header) to current heading node according to
        the current level and position
        """
        # alternate the listing headers. recylce if needed
        list_type = (self.level - 1) % ListTypes.OPTIONS
        if list_type is ListTypes.NUMBER:
            return str(self.position + 1)
        elif list_type is ListTypes.ALPHA:
            return chr(ord('A') + self.position)
        elif list_type is ListTypes.ROMAN:
            return ListTypes.convertRoman(self.position + 1)
        elif list_type is ListTypes.LOWALPHA:
            return chr(ord('a') + self.position)
        elif list_type is ListTypes.STAR:
            return "*"
        else:
            return '+'


class Paragraph(Node):
    """
    Paragraph Node that should be the leaf node (Child of Node class)

    @attributes
    Base attributes
    +
    level - always set to maxint (leaf)
    """

    def __init__(self, content):
        super(Paragraph, self).__init__(content)
        self.level = sys.maxint


class Document(Node):
    """
    Documen Node that is the base node for a document (Child of Node class)

    @attributes
    Base attributes
    content for document node is interpreted as the name of the document
    level - always set to  0, base level
    """

    def __init__(self, name):
        super(Document, self).__init__(name)
        self.level = 0

    def display_outline(self):
        """
        DFS traverse to demonstrate the outline of current document
        print to sdt
        """
        from collections import deque
        stack = deque()
        stack.append(self)
        while stack:
            cur = stack.pop()
            # Display document name
            if type(cur) is Document:
                output = cur.name
            # display outline with proper format
            else:
                output = "%s%s. %s" % (' ' * cur.level, cur.outline_prefix,
                                       cur.content)
            print output
            # continue the DFS
            for i in xrange(len(cur.children) - 1, -1, -1):
                if type(cur.children[i]) is not Paragraph:
                    stack.append(cur.children[i])

    def hasOutline(self):
        if self.children:
            return type(self.children[0]) is Heading
        else:
            return False

    def setName(self, name):
        """
        Set the name of the docuemnt
        """
        self.content = name

    @property
    def name(self):
        """
        GET the name of the document
        """
        return self.content


class Parser(object):
    """
    Parser Engine to parse document file
    PROHIBITED to be Instantiated

    @class attributes
    base_node - base document node (one for each parsing run)
    parent_node - parent_node of the current node
    current_node - current tokenized node
    NEWNODE - Indicates tokenize method returns a NEWNODE
    EXPANDNODE - indicates tokenize method EXPANDED previous node
    """

    base_node, parent_node, current_node = None, None, None
    NEWNODE, EXPANDNODE = True, False

    def __init__(*args, **kwargs):
        """
        PROHIBIT class from Instantiation
        @raise
        ParserError
        """
        raise ParserError("Parser is an Engine, Donot Instantiate this Class")

    @classmethod
    def tokenize(cls, line):
        """
        tokenize a string to corresponding node
        @parameter
        raw string represents a token
        @return
        None
        @side-effect
        Set class attribute to be parsed node(Heading/Pargraph) from raw string
        @raise
        Tokenization Error
        """
        tokens = line.split()
        # Heading
        if tokens[TokenIndexes.IDENTITY] == "HEADING":
            cls.current_node = Heading(int(tokens[TokenIndexes.HEADING_LEVEL]),
                                       ' '.join(tokens[TokenIndexes.HEADING_CONTENT:]))
            return cls.NEWNODE
        # Paragraph
        elif tokens[TokenIndexes.IDENTITY] == "PARAGRAPH":
            cls.current_node = Paragraph(' '.join(tokens[TokenIndexes.PARAGRAPH_CONTENT:]))
            return cls.NEWNODE
        # Continue Content
        elif line.startswith(' '):
            cls.current_node.expandContent(' '.join(tokens))
            return cls.EXPANDNODE
        else:
            raise TokenizationError("Unexpected Token Size")

    @classmethod
    def parse(cls, document, document_name="New Document"):
        """
        Main method to parse document
        @parameter
        document - opened file (StringIO accpeted)
        [optional]dcoument_name - name of the document
        @return
        return the base document node that represents the parsed document tree
        @raise
        ParserError
        """
        cls.base_node = Document(document_name)
        cls.parent_node = cls.base_node
        counter = 0

        while document.pos != document.len:
            counter += 1
            line = document.readline()
            try:
                if cls.tokenize(line):
                    # Find the correct parent
                    if type(cls.current_node) is Heading and type(cls.parent_node)\
                            is not Document:
                        current_level = cls.current_node.level
                        if current_level > cls.parent_node.level + 1:
                            raise ParserError("Incorrect Format, heading level"
                                              " advanced more than one")

                        while cls.parent_node.level != current_level - 1:
                            cls.parent_node = cls.parent_node.parent
                    # wire parent and child node
                    cls.parent_node.addChild(cls.current_node)
                    cls.current_node.addParent(cls.parent_node)
                    # advance parent node
                    cls.parent_node = cls.current_node

            except TokenizationError as e:
                print "cannot parse the document,"  \
                    "check the document format, failed @%d" % counter
                raise e

            except ParserError as e:
                print "cannot parse the document," \
                    "check the document format, failed @%d" % counter
                raise e
        document.close()

        return cls.base_node

if __name__ == '__main__':

    test_success_1 = 'HEADING 1  All About Birds\n'\
        'HEADING 2  Kinds of Birds\n'\
        'HEADING 3  The Finch\n'\
        'PARAGRAPH  The true finches are small to medium\xc2\xadsized passerine birds in\n'\
        '           the family Fringillidae.\n'\
        'HEADING 3  The Swan\n'\
        'PARAGRAPH  Swans are birds of the family Anatidae within the genus Cygnus.\n'\
        'HEADING 2  Habitats\n'\
        'HEADING 3  Wetlands\n'\
        'PARAGRAPH  A wetland is a land area that is saturated with water, either\n'\
        '           permanently or seasonally, such that it takes on the\n'\
        '           characteristics of a distinct ecosystem.\n'
    mock_file_success_1 = StringIO(test_success_1)
    print "Test Case 1 -- Successful Birds(test_success_1)"
    print "--------------------------------"
    print "Original File\n++++++++++++++++++++++++++++++\n%s\n" % test_success_1

    document = Parser.parse(mock_file_success_1, "Successful Birds")
    print "Parsed Resulting Document Tree\n++++++++++++++++++++++++++++++"
    if document.hasOutline():
        document.display_outline()

    print("\n\n====================================================\n\n")

    test_success_2 = 'HEADING 1  All About Dogs\n'\
        'HEADING 2  Kinds of Dogs\n'\
        'HEADING 3  The Shiba\n'\
        'PARAGRAPH  The true Shiba are blablabla\xc2\xadsized passerine birds in\n'\
        '           the family Fringillidae.\n'\
        'HEADING 3  The Jiangou\n'\
        'PARAGRAPH  JIANGOU are DOGS of the family Anatidae within the genus Cygnus.\n'\
        'HEADING 3  The RenxingGou\n'\
        'HEADING 2  Habitats\n'\
        'HEADING 3  House\n'\
        'HEADING 4  MyHouse\n'\
        "HEADING 4  Matt's House'\n"\
        "HEADING 5  Matt's Winter House\n"\
        "HEADING 6  First Floor\n"\
        "HEADING 7  Second Room\n"\
        "HEADING 8  Queen Size Bed\n"\
        "HEADING 6  Second Floor\n"\
        "HEADING 7  First Room\n"\
        "HEADING 8  King Size Bed\n"\
        "HEADING 4  Matt's Summer House\n"\
        "HEADING 3  Trash Cans\n"\
        "HEADING 1  Extra Things About Dogs\n"\
        "HEADING 2  Noboday likes cat\n"\
        "HEADING 2  Who Let the DOGS OUT\n"

    mock_file_success_2 = StringIO(test_success_2)
    print "Test Case 2 -- Charming Dogs(test_success_2)"
    print "--------------------------------"
    print "Original File\n++++++++++++++++++++++++++++++\n%s\n" % test_success_2

    document = Parser.parse(mock_file_success_2, "Charming Dogs")
    print "Parsed Resulting Document Tree, Should Have Recycled Listing " \
          "Header\n++++++++++++++++++++++++++++++++++++++++++++++++++++"
    if document.hasOutline():
        document.display_outline()

    print("\n\n====================================================\n\n")

    test_success_3 = 'PARAGRAPH  The true Promise are blablabla\xc2\xadsized'
    mock_file_success_3 = StringIO(test_success_3)
    print "Test Case 3 -- Empty Promise(test_document_without_outline)"
    print "--------------------------------"
    print "Original File\n++++++++++++++++++++++++++++++\n%s\n" % test_success_3

    document = Parser.parse(mock_file_success_3, "Empty Promise")
    print "Parsed Resulting Document Tree(Should be Empty)\n"\
        "++++++++++++++++++++++++++++++++++"
    if document.hasOutline():
        document.display_outline()

    print "Expecting hasOutline return False, did it?   %s\n" \
        % ('NO' if document.hasOutline() else "YES")

    print "But it should Have PARAGRAPH without Outline"\
          "\n+++++++++++++++++++++++++++++++++++++++++ \n%s\n%s"\
        % (document.name, str(document.children[0]))

    print("\n\n====================================================\n\n")

    test_failure_1 = 'HEADING 1  All About Monkeys\n'\
        'HEADING 2  Kinds of Monkeys\n'\
        'FAIL 4  The Shiba\n'\
        'PARAGRAPH  The true Shiba are blablabla\xc2\xadsized passerine birds in\n'\
        '           the family Fringillidae.\n'\
        'HEADING 3  The Jiangou\n'\

    mock_file_failure_1 = StringIO(test_failure_1)
    print "Test Case 4 -- Failure Moenkeys(test_failure_1-tokenization error)"
    print "--------------------------------"
    print "Original File\n++++++++++++++++++++++++++++++\n%s\n" % test_failure_1
    try:
        print "Parsing Result Should Fail\n++++++++++++++++++++++++++++++"
        document = Parser.parse(mock_file_failure_1, "Failure Monkeys")
    except Exception as e:

        print type(e), e
        print "Expecting TokenizationError did we get it    %s" \
            % ('YES' if type(e) is TokenizationError else 'NO')

    print("\n\n====================================================\n\n")

    test_failure_2 = 'HEADING 1  All About Seeds\n'\
        'HEADING 2  Kinds of Seeds\n'\
        'HEADING 4  The Shiba\n'\
        'PARAGRAPH  The true Shiba are blablabla\xc2\xadsized passerine birds in\n'\
        '           the family Fringillidae.\n'\
        'HEADING 3  The Jiangou\n'\

    mock_file_failure_2 = StringIO(test_failure_2)
    print "Test Case 5 -- Stupid Seeds(test_failure_2-Parser error)"
    print "--------------------------------"
    print "Original File\n++++++++++++++++++++++++++++++\n%s\n" % test_failure_2

    try:
        print "Parsing Result Should Fail\n++++++++++++++++++++++++++++++"
        document = Parser.parse(mock_file_failure_2, "Stupid Seeds")
    except Exception as e:
        print type(e), e
        print "Expecting ParserError,  did we get it?   %s" \
            % ('YES' if type(e) is ParserError else 'NO')

    print("\n\n====================================================\n\n")

    print "Test Case 6 -- Forbidden Instantiation(test_failure_3-Parser Error)"
    print "------------------------------------------------------------"
    try:
        print "Instantiation Should Fail \n +++++++++++++++++++++"
        parser = Parser()
    except Exception as e:
        print type(e), e
        print "Expect prohibiting User from Instantiation, did it?  %s"\
            % ("YES" if type(e) is ParserError else "NO")
