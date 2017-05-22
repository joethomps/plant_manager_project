from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from django.conf import settings
from reportlab.pdfbase.pdfmetrics import stringWidth
from batches.models import Drop

def createDocket(b):
    # retrieve list of drops for batch in correct order
    drops = b.drop_set.order_by('no_in_batch')
    no_drops = drops.count()

    # dictionary of the information to be printed on the ticket
    d1 = {'Name:': str(b.client),
         'Delivery Address:': [str(b.deliv_addr_1),
                              str(b.deliv_addr_2),
                              str(b.deliv_addr_3),
                              str(b.deliv_addr_4),
                              str(b.eircode)]}
    d2 = {'Date:': str(drops[0].end_datetime.date()),
         'Time of Loading:': str(drops[no_drops-1].end_datetime.time()),
         'Driver:': str(b.driver),
         'Truck Reg.:': str(b.truck)}
    d3 = {'order_ref': 'ORD' + str(b.batch_no),
         'prod_code': str(b.recipe.name),
         'description': str(b.recipe.description),
         'quantity': str(b.volume) + ' m^3',
         }

    # initialise canvas object for ticket
    filename = 'b' + str(b.batch_no).zfill(8) + '.pdf'
    filepath = settings.MEDIA_ROOT + '\\' + filename
    p = canvas.Canvas(filepath, pagesize=A4)
    pw, ph = A4
    p.setTitle('Delivery Ticket')
    p.setLineWidth(0.5)

    marg = {'l':20, 'r':20, 't':10, 'b':10}
    w = pw-marg['l']-marg['r']
    h = ph-marg['t']-marg['b']
    p.translate(marg['l'], marg['b'])
    #p.setStrokeColorRGB(0.2,0.5,0.3)
    #p.setFillColorRGB(1, 1, 1)
    
    # draw title in top corner
    ct = cursor(p,w,h-14,size=14)
    ct.write('DELIVERY TICKET', align='right')

    # Header
    ch = cursor(p,0,h-20,size=20)
    ch.write('FOGARTY CONCRETE')
    ch.size = 12; ch.newline();
    ch.listwrite(['Gurrane, Templederry, Nenagh, Co. Tipperary',
               'Telephone: 0504-52151  Fax: 0504-52957',
               'Mobile: 087-2831415 (Andy), 086-3813399 (Plant)',
               'Email: andrewfogarty@eircom.net'])

    c1 = cursor(p,0,0,size=12,font='Helvetica')
    c2 = cursor(p,0,0,size=12,ls=0.3,font='Courier')
    
    t1 = table(p,
               left=0,
               top=h-120,
               row_heights=[20, 120],
               col_widths=[w/2, w/2],
               )
    t1.place_cursor(c1,1,1); c1.write('Client')
    t1.place_cursor(c1,1,2); c1.write('Loading')
    t1.place_cursor(c2,2,1); c2.dictwrite(d1)
    t1.place_cursor(c2,2,2); c2.dictwrite(d2)

    t2 = table(p,        
               left=t1.left,
               top=t1.bottom,
               row_heights=[20,60],
               col_widths=[w/6, w/6, w/2, w/6],
               bord_t=False,
               )
    t2.place_cursor(c1,1,1); c1.write('Order Ref')
    t2.place_cursor(c1,1,2); c1.write('Product Code')
    t2.place_cursor(c1,1,3); c1.write('Description')
    t2.place_cursor(c1,1,4); c1.write('Quantity')
    t2.place_cursor(c2,2,1); c2.write(d3['order_ref'])
    t2.place_cursor(c2,2,2); c2.write(d3['prod_code'])
    t2.place_cursor(c2,2,3); c2.write(d3['description'])
    t2.place_cursor(c2,2,4); c2.write(d3['quantity'])

    t3 = table(p,        
               left=t2.left,
               top=t2.bottom,
               row_heights=[20,120],
               col_widths=[w/2,w/2],
               bord_t=False,
               )
    t3.place_cursor(c1,1,1); c1.write('Composition')
    t3.place_cursor(c1,1,2); c1.write('On Site')
    
    t4 = table(p,        
               left=t3.left,
               top=t3.bottom,
               row_heights=[20,120],
               col_widths=[w],
               bord_t=False,
               )
    t4.place_cursor(c1,1,1); c1.write('Customer')
    
    # draw logos on the page
    nsaiHeight = 25*mm
    nsaiWidth = nsaiHeight*167/237
    drawLogo(p,w-nsaiWidth,h-nsaiHeight-25,'nsai_logo.jpg',nsaiHeight,nsaiWidth)

    icfWidth = nsaiHeight*142/146
    drawLogo(p,w-nsaiWidth-icfWidth-15,h-nsaiHeight-25,'icf_logo.jpg',nsaiHeight,icfWidth)

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

    def place_cursor(self, cur, row, col, font='Helvetica', size=12, gap=3):
        cur.x = self.left + sum(self.col_w[0:col-1]) + gap
        cur.y = self.top - sum(self.row_h[0:row-1]) - size - gap
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
    
    def __init__(self, canvas, start_x, start_y, font='Helvetica', size=12, ls=0.5):
        self.c = canvas
        self.x = start_x
        self.y = start_y
        self.font = font
        self.size = size
        self.ls = ls
        self.reset()

    def reset(self):
        self.x_home = self.x
        self.y_home = self.y
        
    def write(self,text_string,align='left'):
        self.c.setFont(self.font, self.size)
        w = stringWidth(text_string, self.font, self.size)
        if align == 'right':
            self.c.drawString(self.x-w, self.y, str(text_string))
        elif align == 'centre':
            self.c.drawString(self.x-w/2, self.y, str(text_string))
            self.x += w/2
        else:
            self.c.drawString(self.x, self.y, str(text_string))
            self.x += w

    def listwrite(self,text_string_list,align='left'):
        for string in text_string_list:
            self.write(string,align=align)
            self.newline()

    def dictwrite(self,text_string_dict,key_font='Helvetica'):
        val_font = self.font
        for key, val in text_string_dict.items():
            self.font = key_font
            self.write(key)
            self.space()
            self.font = val_font
            val_x = self.x
            if not isinstance(val,list):
                val = [val]
            for line in val:
                self.x = val_x
                self.write(line)
                self.newline()
        
    def space(self):
        self.write(' ')

    def newline(self):
        self.x = self.x_home
        self.y += -(1+self.ls)*self.size

    

