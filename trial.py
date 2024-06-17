from bs4 import BeautifulSoup

soup = '''
<BODY BGCOLOR="lightyellow">
<HTML>
<HEAD>
<TITLE>General Electives</TITLE>
</HEAD>
<BODY>
<CENTER><FONT SIZE=4 FACE="Arial">
<B><CENTER><B><FONT SIZE=2 COLOR=black>Search Result : "SC4061" for 2024 Semester 1</FONT></B></B>
</FONT>
<BR>
<FONT SIZE=2 FACE="Arial">

</FONT></center>
<HR SIZE=2>
<TABLE >
<TR>
<TD WIDTH="100"><FONT SIZE=2><B>COURSE CODE</B></TD>
<TD WIDTH="400"><FONT SIZE=2><B>TITLE</B></TD>
<TD WIDTH="100"><FONT SIZE=2><B>AU</B></TD>
<TD WIDTH="100"><FONT SIZE=2><B>PROGRAMME/(DEPT MAINTAIN*)</FONT></B></TD>
</TR>
<TR>
<TD WIDTH="100"><B><FONT SIZE=2 COLOR=#0000FF>SC4061</FONT></B></TD>
<TD WIDTH="400"><B><FONT SIZE=2 COLOR=#0000FF>COMPUTER VISION</FONT></B></TD>
<TD WIDTH="100"><B><FONT SIZE=2 COLOR=#0000FF>  3.0</FONT></B></TD>
<TD WIDTH="100"><B><FONT SIZE=2 COLOR=#0000FF>CSC(CE)</FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=#FF00FF>Prerequisite:</FONT></B></TD>
<TD COLSPAN="2"><B><FONT SIZE=2 COLOR=#FF00FF>Year 3 standing</FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=#FF00FF></FONT></B></TD>
<TD COLSPAN="2"><B><FONT  SIZE=2 COLOR=#FF00FF></FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=BROWN>Mutually exclusive with: </FONT></B></TD>
<TD COLSPAN="2"><B><FONT SIZE=2 COLOR=BROWN>CE4003, CZ4003</FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=GREEN>Not available to Programme: </FONT></B></TD>
<TD COLSPAN="2"><B><FONT SIZE=2 COLOR=GREEN>EEE, EEEC, IEEC, IEM</FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=GREEN>Not available to all Programme with: </FONT></B></TD>
<TD COLSPAN="2"><B><FONT SIZE=2 COLOR=GREEN>(Admyr 2011-2020)</FONT></B></TD>
</TR>
<TR>
<TD><B><FONT SIZE=2 COLOR=GREEN>Not available as PE to Programme: </FONT></B></TD>
<TD COLSPAN="2"><B><FONT SIZE=2 COLOR=GREEN>REP(ASEN), REP(BIE), REP(CBE), REP(CVEN), REP(EEE), REP(ENE), REP(MAT), REP(ME)</FONT></B></TD>
</TR>
<TR>
<TD COLSPAN="3"><B><FONT SIZE=2 COLOR=BLUE>Not offered as Unrestricted Elective </FONT></B></TD>
</TR>
<TR>
<TD WIDTH="650" colspan="4"><FONT SIZE=2>
Image formation and segmentation. Image acquisition. Image representations and organisations. Digital image characterisation. Image enhancement and restoration. Image coding and data compression. Geometry for 3D vision. Pattern recognition using neural networks. Image analysis and understanding. Machine vision applications.

</TD>
</TR>
<TR>
<TD>&nbsp;</TD>
</TR>
</TABLE>
</CENTER>
</FORM>
</BODY>
</HTML>
'''
soup = BeautifulSoup(soup, 'html.parser')

description_td = soup.find_all('td')[-2]
description = description_td.text.strip()

# Function to find the text in a specific TR
def get_tr_text(soup, search_text):
    trs = soup.find_all('tr')
    for tr in trs:
        td = tr.find('td')
        if td and search_text in td.get_text():
            tds = tr.find_all('td')
            if len(tds) > 1:
                return tds[1].get_text(strip=True)
    return None

# Extracting required information
mutually_exclusive = get_tr_text(soup, 'Mutually exclusive with:')
prerequisite = get_tr_text(soup, 'Prerequisite:')
not_available = get_tr_text(soup, 'Not available to Programme:')
not_available_all = get_tr_text(soup, 'Not available to all Programme with:')

tds = soup.find_all('td')
for td in tds:
    if 'Not offered as Unrestricted Elective' in td.get_text():
        print('not offered as UE')
    if 'Not offered as Broadening and Deepening Elective' in td.get_text():
        print('not offered as BDE')

# Printing extracted values
print(f"Course: SC4061")
print(f"Description: {description}")
print(f"Mutually Exclusive: {mutually_exclusive}")
print(f"Prerequisite: {prerequisite}")
print(f"Not Available to Programme: {not_available}")
print(f"Not Available to all Programme with: {not_available_all}")
