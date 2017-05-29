from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from django.conf import settings
from django.db.models import Sum
from reportlab.pdfbase.pdfmetrics import stringWidth
from batches.models import Drop, Recipe_Detail, Ingredient
from django.db.models import Max, Sum, Avg, F

def createDocket(b):
    r = b.recipe 

    # initialise canvas object for ticket
    filename = 'b' + str(b.batch_no).zfill(8) + '.pdf'
    filepath = settings.MEDIA_ROOT + '\\' + filename
    p = canvas.Canvas(filepath, pagesize=A4)
    pw, ph = A4
    p.setTitle('Delivery Ticket')
    p.setLineWidth(0.5)

    # margins setup
    marg = {'l':20, 'r':20, 't':10, 'b':10}
    w = pw-marg['l']-marg['r']
    h = ph-marg['t']-marg['b']
    p.translate(marg['l'], marg['b'])
        # p.setStrokeColorRGB(0.2,0.5,0.3)
        # p.setFillColorRGB(1, 1, 1)
    
    # draw title in top corner
    ct = cursor(p,w,h-14,size=14)
    ct.write('DELIVERY TICKET', align='r')

    # Name and Address
    ch = cursor(p,0,h-20,size=20)
    ch.write('FOGARTY CONCRETE')
    ch.size = 12; ch.newline();
    ch.listwrite([
        ['Gurrane, Templederry, Nenagh, Co. Tipperary'],
        ['Telephone: 0504-52151  Fax: 0504-52957'],
        ['Mobile: 087-2831415 (Andy), 086-3813399 (Plant)'],
        ['Email: andrewfogarty@eircom.net']
               ])

    c1 = cursor(p,0,0,size=12,font='Helvetica')
    c2 = cursor(p,0,0,size=12,ls=0.65,font='Courier')
    
    t1 = table(p,
               left=0,
               top=h-110,
               row_heights=[22, 150],
               col_widths=[w/2, w/2],
               )
    t1.place_cursor(c1,1,1);
    c1.write('Client')
    t1.place_cursor(c1,1,2);
    c1.write('Loading')
    t1.place_cursor(c2,2,1);
    c2.listwrite((
        ('Name:', str(b.client)),
        ('Delivery Address:', b.deliv_addr_1, b.deliv_addr_2, b.deliv_addr_3, b.deliv_addr_4, b.eircode)
        ))
    t1.place_cursor(c2,2,2);
    c2.listwrite((
        ('Date:', str(b.start_datetime().date())),
        ('Time of Loading:', str(b.end_datetime().time())),
        ('Driver:', b.driver.name),
        ('Truck Reg.:', b.truck.reg)
        ))

    t2 = table(p,        
               left=t1.left,
               top=t1.bottom,
               row_heights=[22,80],
               col_widths=[w/6, w/6, w/2, w/6],
               bord_t=False,
               )
    t2.place_cursor(c1,1,1)
    c1.write('Batch No.')
    t2.place_cursor(c1,1,2)
    c1.write('Product Code')
    t2.place_cursor(c1,1,3)
    c1.write('Description')
    t2.place_cursor(c1,1,4)
    c1.write('Quantity')
    t2.place_cursor(c2,2,1)
    c2.write(str(b))
    t2.place_cursor(c2,2,2)
    c2.write(r.get_strength_class_display())
    t2.place_cursor(c2,2,3)
    c2.wrap_write(r.description,32)
    t2.place_cursor(c2,2,4)
    c2.write('%.1f m^3' % (b.volume))

    t3 = table(p,        
               left=t2.left,
               top=t2.bottom,
               row_heights=[22,260],
               col_widths=[w/2,w/2],
               bord_t=False,
               )
    t3.place_cursor(c1,1,1)
    c1.write('Composition')
    t3.place_cursor(c1,1,2)
    c1.write('On Site')
    t3.place_cursor(c2,2,1)
    c2.listwrite((
        ('Admixtures:',) + tuple(r.admixtures_as_list()),
        ('Slump:', r.get_slump_class_display()),
        ('Max Agg Size (D):', '%i mm' % (r.aggregate_D())),
        ('Min. Cement Content:', '%.0f kg/m^3' % (r.total_cement())),
        ('Cement Type:', ', '.join(r.cement_types_as_list())),
        ('Max W/C Ratio:', '%.2f' % (r.wc_ratio())),
        ('Exposure Class:', ', '.join(r.exp_classes_as_list())),
        ('Cl Content Class:', r.get_cl_content_class_display()),
        ))
    c2.width = 0.96*w/2
    c2.ls = 1.2
    t3.place_cursor(c2,2,2)
    c2.listwrite((
        ('Time On Site:','-...'),
        ('Time Off Loaded:','-...'),
        ('Amount Conveyered:','-...'),
        ('Water Added (Supplier)','-...'),
        ('','-...'),
        ('Extra Water Added',''),
        ('at Customers Instruction:','-...'),
        ('','-...'),
        ('Estimated Slump:','-...'),
             ))
    
    t4 = table(p,        
               left=t3.left,
               top=t3.bottom,
               row_heights=[22],
               col_widths=[w],
               bord_t=False,
               )
    t4.place_cursor(c1,1,1); c1.write('Customer')

    t5 = table(p,        
               left=t4.left,
               top=t4.bottom,
               row_heights=[85,35],
               col_widths=[w/2],
               bord_t=False,
               )
    t5.place_cursor(c1,1,1)
    c1.listwrite([
        ['-Caution: Prolongled skin contact with'],
        ['wet concrete can result in cement burns'],
        ['-Where contact occurs wash thoroughly!'],
        ['-Material safety data sheet available upon request'],
               ])
    t5.place_cursor(c1,2,1,align='cl')
    c1.write('Conforms to EN-206-1:   ');
    c1.write('Yes '); c1.checkbox(); c1.write('   No '); c1.checkbox()

    t6 = table(p,        
               left=t5.right,
               top=t5.top,
               row_heights=[sum(t5.row_h)],
               col_widths=[w/2],
               bord_t=False,
               bord_l=False
               )
    t6.place_cursor(c1,1,1,align='tc')
    c1.width = 0.96*w/2
    c1.ls = 0.65
    c1.listwrite([
        ['Received in good order and condition'],
        ['Customer/Representative signature:'],
        ['...'],
        [''],
        ['...'],
               ], align='c')
    
    # draw logos on the page
    nsaiHeight = 25*mm
    nsaiWidth = nsaiHeight*167/237
    drawLogo(p,w-nsaiWidth,h-nsaiHeight-25,'nsai_logo.jpg',nsaiHeight,nsaiWidth)

    icfWidth = nsaiHeight*142/146
    drawLogo(p,w-nsaiWidth-icfWidth-15,h-nsaiHeight-25,'icf_logo.jpg',nsaiHeight,icfWidth)

    ceHeight = 10*mm
    ceWidth = ceHeight*500/350
    drawLogo(p,w-nsaiWidth-icfWidth-ceWidth-30,h-nsaiHeight-25,'ce_logo.jpg',ceHeight,ceWidth)

    # finish page, save and return filepath
    p.showPage()
    p.save()
    return filepath
            
def drawLogo(p,x,y,logo,height,width):
    logoHeight = height
    logoWidth = width
    img = ImageReader(settings.MEDIA_ROOT + '\\' + logo)
    p.drawImage(img, x, y, height=logoHeight, width=logoWidth)

class table:
    """For drawing tables with borders and finding the coordinates to write inside"""
    """(c) Joseph Thompson 2017"""

    def __init__(self, canvas, left, top, row_heights, col_widths, draw=True, bord_t=True, bord_b=True, bord_l=True, bord_r=True):
        self.c = canvas
        self.row_h = row_heights
        self.col_w = col_widths
        self.nrows = len(row_heights)
        self.ncols = len(col_widths)
        self.left = left
        self.top = top
        self.bottom = self.top-sum(self.row_h)
        self.right = self.left+sum(self.col_w)
        if draw == True:
            self.draw(bord_t, bord_b, bord_l, bord_r)

    def place_cursor(self, cur, row, col, font='Helvetica', gap=4, align='tl'):
        s = cur.size
        v_align = align[0];
        h_align = align[1];
        l = self.left + sum(self.col_w[0:col-1])
        r = self.left + sum(self.col_w[0:col])
        t = self.top - sum(self.row_h[0:row-1])
        b = self.top - sum(self.row_h[0:row])
        if h_align == 'c':
            cur.x = (l + r)/2
        elif h_align == 'r':
            cur.x = r - gap
        else:
            cur.x = l + gap
        if v_align == 'c':
            cur.y = (t + b - s)/2
        elif v_align == 'b':
            cur.y = b + gap
        else:
            cur.y = t - s - gap        
        cur.reset()

    def draw(self, t=True, b=True, l=True, r=True):
        for i in range(t==False,self.nrows+(b==True)):
            self.c.line(self.left,                  self.top-sum(self.row_h[0:i]),
                        self.right,  self.top-sum(self.row_h[0:i]))
        for i in range(l==False,self.ncols+(r==True)):
            self.c.line(self.left+sum(self.col_w[0:i]), self.top,
                        self.left+sum(self.col_w[0:i]), self.bottom)
        
class cursor:
    """Simple cursor for writing text on canvas"""
    """(c) Joseph Thompson 2017"""
    
    def __init__(self, canvas, start_x, start_y, font='Helvetica', size=12, ls=0.5, width=80):
        self.c = canvas
        self.x = start_x
        self.y = start_y
        self.font = font
        self.size = size
        self.ls = ls
        self.reset()
        self.width = width

    def reset(self):
        self.x_home = self.x
        self.y_home = self.y

    def wrap_write(self, text_string, max_length, align='l'):
        from textwrap import wrap
        lines = wrap(text_string, max_length, break_long_words=True)
        line_list = [[line] for line in lines]
        self.listwrite(line_list, align=align)
        
    def write(self,text_string,align='l'):
        def start_x(x,w,align):
            if align == 'r':
                return x-w
            elif align == 'c':
                return x-w/2
            else:
                return x 
        self.c.setFont(self.font, self.size)
        s = self.size
        if text_string == '-...':
            w = self.width
            x = start_x(self.x,w,align)
            self.c.setDash(1,2)
            self.c.line(x,              self.y-s/4.0,
                        self.x_home+w,  self.y-s/4.0)
            self.c.setDash(1)
        elif text_string == '...':
            w = self.width
            x = start_x(self.x,w,align)
            self.c.setDash(1,2)
            self.c.line(x,              self.y-s/4.0,
                        x+w,  self.y-s/4.0)
            self.c.setDash(1) 
        else:
            w = stringWidth(text_string, self.font, self.size)
            x = start_x(self.x,w,align)
            self.c.drawString(x, self.y, str(text_string))
        self.x = x + w 

    def listwrite(self,string_list_list,align='l',key_font='Helvetica'):
        val_font = self.font
        for string_list in string_list_list:
            if len(string_list) == 0:
                self.newline()    
            elif len(string_list) == 1:
                self.write(string_list[0], align=align)
                self.newline()
            else:
                self.font = key_font
                self.write(string_list[0], align=align)
                self.write('  ')
                self.font = val_font
                val_x = self.x
                for i in range(1,len(string_list)):
                    self.x = val_x
                    self.write(string_list[i], align=align)
                    self.newline()

    def newline(self):
        self.x = self.x_home
        self.y += -(1+self.ls)*self.size

    def checkbox(self):
        s = self.size
        self.c.rect(self.x, self.y-s/4.0, s*1.25, s*1.25)
        self.x += s*1.25
