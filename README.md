"""
#### Description

This is a StackOverFlow  post asking about how to parse a document

Original question
_______________________
Document management system, input documents are structured with weighted headings.

Sample Input
+++++++++++++++++++++++
HEADING 1  All About Birds
HEADING 2  Kinds of Birds
HEADING 3  The Finch
PARAGRAPH  The true finches are small to medium-sized passerine birds in
           the family Fringillidae.
HEADING 3  The Swan
PARAGRAPH  Swans are birds of the family Anatidae within the genus Cygnus.
HEADING 2  Habitats
HEADING 3  Wetlands
PARAGRAPH  A wetland is a land area that is saturated with water, either
           permanently or seasonally, such that it takes on the
           characteristics of a distinct ecosystem.

Sample output
++++++++++++++++++++++
1. All About Birds
  A. Kinds of Birds
i. The Finch
    ii. The Swan
  B. Habitats
i. Wetlands


#### Approach
_____________________
Use
Node -> Document(node)
     -> Heading(node)
     -> Pargraph(node)
to represent the parsed document tree

Construct
Parser Engine to parse the document

See classes for detailed explanation

#### Assumptions
____________________
1. a document can be correctly parsed without outline

document ->paragraph
         ->paragraph

2. Heading node must advance at most 1 level at a time
3. One document can have multiple header 1

#### TestCases
____________________
6 test cases are demonstrated in the main driver
"""
