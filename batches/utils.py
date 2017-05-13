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
    d = {'client': str(b.client),
         'deliv_addr_1': str(b.deliv_addr_1),
         'deliv_addr_2': str(b.deliv_addr_2),
         'deliv_addr_3': str(b.deliv_addr_3),
         'deliv_addr_4': str(b.deliv_addr_4),
         'eircode': str(b.eircode),
         'date': str(drops[0].end_datetime.date()),
         'load_time': str(drops[no_drops-1].end_datetime.time()),
         'driver': str(b.driver),
         'truck_reg': str(b.truck),
         'order_ref': 'ORD' + str(b.batch_no),
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
    c1 = cursor(p,w,h-14,size=14)
    c1.write('DELIVERY TICKET', align='right')

    c2 = cursor(p,0,h-20,size=20)
    c2.write('FOGARTY CONCRETE')
    c2.size = 12
    c2.newline(); c2.write('Gurrane, Templederry, Nenagh, Co. Tipperary')
    c2.newline(); c2.write('Telephone: 0504-52151  Fax: 0504-52957')
    c2.newline(); c2.write('Mobile: 087-2831415 (Andy), 086-3813399 (Plant)')
    c2.newline(); c2.write('Email: andrewfogarty@eircom.net')

    c2.ls = 0.3
    t1 = table(p,
               left=0,
               top=h-120,
               row_heights=[120],
               col_widths=[w/2, w/2],
               )
    t1.place_cursor(c2,1,1)
    c2.font = 'Helvetica'; c2.write('Client: ')
    c2.font = 'Courier'; c2.write(d['client'])
    c2.newline(); c2.font = 'Helvetica'; c2.write('Delivery Address')
    c2.font = 'Courier'
    c2.newline(); c2.write(d['deliv_addr_1'])
    c2.newline(); c2.write(d['deliv_addr_2'])
    c2.newline(); c2.write(d['deliv_addr_3'])
    c2.newline(); c2.write(d['deliv_addr_4'])
    c2.newline(); c2.write(d['eircode'])

    t1.place_cursor(c2,1,2)
    c2.font = 'Helvetica'; c2.write('Date: ')
    c2.font = 'Courier'; c2.write(d['date'])
    c2.newline(); c2.font = 'Helvetica'; c2.write('Time of Loading: ')
    c2.font = 'Courier'; c2.write(d['load_time'])
    c2.newline(); c2.font = 'Helvetica'; c2.write('Driver: ')
    c2.font = 'Courier'; c2.write(d['driver'])
    c2.newline(); c2.font = 'Helvetica'; c2.write('Truck Reg: ')
    c2.font = 'Courier'; c2.write(d['truck_reg'])
        
    t2 = table(p,        
               left=t1.left,
               top=t1.bottom,
               row_heights=[20,40],
               col_widths=[w/6, w/6, w/2, w/6],
               bord_t=False,
               )
    c2.font = 'Helvetica'
    t2.place_cursor(c2,1,1); c2.write('Order Ref')
    t2.place_cursor(c2,1,2); c2.write('Product Code')
    t2.place_cursor(c2,1,3); c2.write('Description')
    t2.place_cursor(c2,1,4); c2.write('Quantity')
    c2.font = 'Courier'
    t2.place_cursor(c2,2,1); c2.write(d['order_ref'])
    t2.place_cursor(c2,2,2); c2.write(d['prod_code'])
    t2.place_cursor(c2,2,3); c2.write(d['description'])
    t2.place_cursor(c2,2,4); c2.write(d['quantity'])

    t3 = table(p,        
               left=t2.left,
               top=t2.bottom,
               row_heights=[20,60],
               col_widths=[w],
               bord_t=False,
               )
    c2.font = 'Helvetica'
    t3.place_cursor(c2,1,1); c2.write('Composition')
    

    t4 = table(p,        
               left=t3.left,
               top=t3.bottom,
               row_heights=[20,60],
               col_widths=[w],
               bord_t=False,
               )
    c2.font = 'Helvetica'
    t4.place_cursor(c2,1,1); c2.write('On Site')

    t5 = table(p,        
               left=t4.left,
               top=t4.bottom,
               row_heights=[20,60],
               col_widths=[w],
               bord_t=False,
               )
    c2.font = 'Helvetica'
    t5.place_cursor(c2,1,1); c2.write('Customer')
    
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
    
    def __init__(self, canvas, start_x, start_y, font='Helvetica', size=12, line_space=0.5):
        self.c = canvas
        self.x = start_x
        self.y = start_y
        self.font = font
        self.size = size
        self.ls = line_space
        self.reset()

    def reset(self):
        self.x_home = self.x
        self.x_home = self.x
        
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
            
    def space(self):
        self.write(' ')

    def newline(self):
        self.x = self.x_home
        self.y += -(1+self.ls)*self.size

    

