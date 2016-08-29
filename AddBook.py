import OCLC as OCLC
import LCC as LCC
import UpdateSheets
import re

def addBook():

    isbn_s = raw_input('Please enter ISBN: ')
    isbn = ''.join(re.findall('\d', isbn_s))

    xml = OCLC.getXML(('isbn',isbn))
    if xml == None:
        print('Could not find ISBN: %s' % isbn)
    if OCLC.responseCode(xml) == '4':
        xml = OCLC.getSingleFromMulti(xml)
    if xml == None:
        print('Could not find ISBN: %s' % isbn)
    basicInfo = OCLC.getRecord(xml)

    print 'Found volume:'
    if 'title' in basicInfo:
        print('Title: %s' % basicInfo['title'])
    if 'author' in basicInfo:
        print('Author: %s' % basicInfo['author'])
    if 'ddc' in basicInfo:
        print('ddc: %s' % basicInfo['ddc'])

    correct = raw_input('Is this correct? (y/n) ')
    if correct == 'y':
        upload = raw_input('Do you want to add to the spreadsheet? (y/n) ')
        if upload == 'y':
            try:
                writeResult = UpdateSheets.write_book(**basicInfo)
                print 'Added to spreadsheet.'
            except:
                print 'failed write'
            try:
                sortResult = UpdateSheets.sort_ddc()
            except:
                print 'failed sort'
            print ""
        else:
            print 'Iight\n'
    else:
        print 'Tough\n'

def main():
    command = raw_input('Add a book? (y/n) ')
    while command == 'y':
        addBook()

if __name__ == '__main__':
    main()
