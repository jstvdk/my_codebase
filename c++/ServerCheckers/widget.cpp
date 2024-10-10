#include "widget.h"
#include <QList>
#include <iostream>
#include <serverch.h>

using namespace std;



Widget::Widget(QWidget *parent)
    : QWidget(parent)
{
    resize(500,500);
    for (int i=0;i<4;i++)
    {
        for (int j=(i+1)%2 ;j<n;j+=2)
        {
            bla.push_back(QPoint(j,i));
        }
    }
    for (int i=n-1;i>n-5;i--)
    {
        for (int j=(n-i-1)%2;j<n;j+=2)
        {
            whi.push_back(QPoint(j,i));
        }
    }

    int dx=width()/n;
    int dy=width()/n;
    int i=point3.x()/dx;
    int j=point3.y()/dy;
   if(s=="black")
   {
       blad.push_back(QPoint(j,i));  //  mojluvo peredastsa zna4ennya shashki yaky treba peretvorutu v damky;
   }
   if(s=="white")
   {
       whid.push_back(QPoint(j,i));
   }

   // zvyazaly server s widgetom
   networkAccessManager = new ServerCh(this); // this dlya togo sho b koly zakrivavsa server delete avtomty4no viklikaetsa
   connect (networkAccessManager,SIGNAL(myconnected()),SLOT(onmyconnected()));
   connect (networkAccessManager,SIGNAL(mydisconnected()),SLOT(onmydisconnected()));
   connect (networkAccessManager,SIGNAL(clientTurn(QList<QPoint>,QList<QPoint>,QList<QPoint>,QList<QPoint>)),
                                 SLOT(onclientTurn(QList<QPoint>,QList<QPoint>,QList<QPoint>,QList<QPoint>)));

}

Widget::~Widget()
{

}

void Widget::paintEvent(QPaintEvent *pe)
{
    //int i,j,dx,dy;
    const int sizex = width()/n, sizey = height()/n;
    //const int sizechx = 40, sizechy = 40;
    QPainter desk(this);
    QBrush b(QColor(255,255,255));
    QBrush w(QColor(100, 100 ,100));

    QImage black; black.load("black.png");
    QImage white; white.load("white.png");
    QImage blackd; blackd.load("black+.png");
    QImage whited; whited.load("white+.png");

    for (int j = 0; j < n; j++)
    {
        int string = sizey*j;
        if (j%2 == 0)
        {
    for (int i = 0; i < n; i++)
    {   if (i%2 == 0)
        {
            desk.setBrush(b);
            desk.drawRect(sizex*i,string,sizex,sizey);
        }
        else
        {
            desk.setBrush(w);
            desk.drawRect(sizex*i,string,sizex,sizey);
        }
    }
        }
        else
            for (int i = 0; i < n; i++)
            {   if (i%2 == 0)
                {
                    desk.setBrush(w);
                    desk.drawRect(sizex*i,string,sizex,sizey);
                }
                else
                {
                    desk.setBrush(b);
                    desk.drawRect(sizex*i,string,sizex,sizey);
                }
            }
    }

/*
     //rozstanovka white
    for (int j = 0; j <= 3; j++)
    {
        if (j == 0 | j == 2 )
    {
            for (int i = 0; i < n/2; i++)
            {
                int coorx = (100*i) + 55;
                int coory = (50*j) + 5;
                desk.drawImage(QRect(coorx,coory, sizechx, sizechy), white);
                wh << QPoint(coorx,coory);
            }
    }
        else
        {
            if (j == 1)
            {
            for (int i = 0; i < n/2; i++)
            {
                int coorx = (100*i) + 5;
                int coory = 55;
                desk.drawImage(QRect(coorx,coory, sizechx, sizechy), white);
                wh << QPoint(coorx,coory);
            }
            }
            else
            {
                for (int i = 0; i < n/2; i++)
                {
                int coorx = (100*i) + 5;
                int coory = 155;
                desk.drawImage(QRect(coorx,coory, sizechx, sizechy), white);
                wh << QPoint(coorx,coory);
                }
            }
        }
}





    // rosstanovka black
    for (int j = 0; j <= 3; j++)
    {
        if (j == 0 | j == 2)
    {
            for (int i = 0; i < n/2; i++)
            {
                int coorx = (100*i) + 55;
                int coory = 305 + (50*j);
                desk.drawImage(QRect(coorx,coory, sizechx, sizechy), black);
            }
    }
        else
        {
            if (j == 1)
            {
            for (int i = 0; i < n/2; i++)
            {
                int coorx = (100*i) + 5;
                int coory = 355;
                desk.drawImage(QRect(coorx,coory, sizechx, sizechy), black);
            }
        }
            else
            {
                for (int i = 0; i < n/2; i++)
                {
                    int coorx = (100*i) + 5;
                    int coory = 300 + (50*j) + 5;
                    desk.drawImage(QRect(coorx,coory, sizechx, sizechy), black);
                }
            }
        }
}

    */

    for (int i= 0;i<bla.size();i++)
    {
        QPoint pos = bla[i];
        int xp = pos.x()*width()/n+5;  // zadae coordinatu de byde malyvatus shashka
        int yp = pos.y()*height()/n+5; //
        desk.drawImage(QRect(xp,yp, width()/n-10,height()/n-10 ), black);
    }

    for (int i= 0;i<whi.size();i++)
    {
        QPoint pos = whi[i];
        int xp = pos.x()*width()/n+5;
        int yp = pos.y()*height()/n+5;
        desk.drawImage(QRect(xp,yp, width()/n-10,height()/n-10 ), white);

    }

    for (int i = 0; i < blad.size(); i++)
    {
        QPoint pos = blad[i];
        int xp = pos.x()*width()/n+5;
        int yp = pos.y()*height()/n+5;
        desk.drawImage(QRect(xp,yp,width()/n-10,height()/n-10 ), blackd);
    }

    for (int i = 0; i < whid.size(); ++i)
    {
        QPoint pos = whid[i];
        int xp = pos.x()*width()/n+5;
        int yp = pos.y()*height()/n+5;
        desk.drawImage(QRect(xp,yp,width()/n-10,height()/n-10), whited);
    }

    int wi=width()/n-10;
    int he=height()/n-10;

    if (s == "black")
    {
        desk.drawImage(QRect(point1.x()-delta.x()-wi/2,point1.y()-delta.y()-he/2,wi,he),black);
    }
    if (s == "white")
    {
        desk.drawImage(QRect(point1.x()-delta.x()-wi/2,point1.y()-delta.y()-he/2,wi,he),white);
    }
    if (s == "black+")
    {
        desk.drawImage(QRect(point1.x()-delta.x()-wi/2,point1.y()-delta.y()-he/2,wi,he),blackd);
    }
    if (s == "white+")
    {
        desk.drawImage(QRect(point1.x()-delta.x()-wi/2,point1.y()-delta.y()-he/2,wi,he),whited);
    }
     //qDebug() << whi;
    // qDebug() << bla;
}

void Widget::mousePressEvent(QMouseEvent *mpe)
{
    if (networkAccessManager -> isConnect() == false) // yaskho nemae zvyazky z managerom to hodyty nemojlyvo
        return;

    int dx = width()/n;
    int dy = width()/n;
    point1 = mpe->pos();
    point0 = point1;
    delta = QPoint(point1.x()-((point1.x()/dx)*dx+dx/2),point1.y()-((point1.y()/dy)*dy+dy/2));  // ?????
    int nx = point1.x()/dx;
    int ny = point1.y()/dy;

    QPoint fs(nx,ny);
    for (int i = 0; i < whi.size(); ++i)
    {
        if ( fs == whi[i] )
            s = "white";
    }
    for (int i = 0; i < bla.size(); ++i)
    {
        if ( fs == bla[i])
            s = "black";
    }
    for (int i = 0; i < whid.size(); ++i)
    {
        if (fs == whid[i])
            s = "white+";
    }
    for (int i = 0; i < blad.size(); ++i)
    {
        if (fs == blad[i])
            s = "black+";
    }
    update();

    //deleting
    for (int i = 0; i < whi.size(); ++i)
    {
        if ( fs == whi[i])
            whi.removeOne(fs);
    }
    for (int i = 0; i < bla.size(); ++i)
    {
        if ( fs == bla[i])
            bla.removeOne(fs);
    }
    for (int i = 0; i < whid.size(); ++i)
    {
        if ( fs == whid[i])
            whid.removeOne(fs);
    }
    for (int i = 0; i < blad.size(); ++i)
    {
        if ( fs == blad[i])
            blad.removeOne(fs);
    }

}

void Widget::mouseMoveEvent(QMouseEvent *mme)
{
    if (networkAccessManager -> isConnect() == false) // yaskho nemae ziednyannya to zavershye gry
        return;
    int dx=width()/n;
    int dy=width()/n;
    point1=mme->pos();
    update();
}

void Widget::mouseReleaseEvent(QMouseEvent *mre)
{
    if (networkAccessManager -> isConnect() == false) // yaskho nemae ziednyannya to zavershye gry
        return;

    point3=mre->pos();
    int dx=width()/n;
    int dy=width()/n;
    int i=point3.x()/dx; // koordinata vkazivnuka mishki v shaskovih koordinatah
    int j=point3.y()/dy;
    int i0=point0.x()/dx;  // po4atkova koordinata shashki
    int j0=point0.y()/dy;

    // perevirka 4y e tam shashka
    QString check;
    for (int k=0;k<bla.size();k++)
    {
        if (bla[k]==QPoint(i,j))
        {
            check="b";
        }
    }
    for (int k=0;k<whi.size();k++)
    {
        if (whi[k]==QPoint(i,j))
        {
            check="w";
        }
    }

    QPoint temp;
    if(                    (i%2==0 && j%2==0)
                         ||(i%2!=0 && j%2!=0)
                         ||(abs(point3.x()/dx-point0.x()/dx)!=abs(point3.y()/dy-point0.y()/dy))
                         ||(check=="b")
                         ||(check=="w"))

    {
        temp=QPoint(point0.x()/dx,point0.y()/dy); // perevirka 4i e tam inshi shashki, abo ???
    }
    else
        temp=QPoint(i,j);

    if(s=="black")
    {
        bla.push_back(temp);
    }
    if(s=="white")
    {
        whi.push_back(temp);
    }
    if(s=="black+")
    {
        blad.push_back(temp);
    }
    if(s=="white+")
    {
        whid.push_back(temp);
    }

    if((s=="black")&&(j==9)&&(check!="b")&&(check!="w"))
    {
        blad.push_back(QPoint(i,j));
        bla.removeOne(QPoint(i,j));
    }
    if((s=="white")&&(j==0)&&(check!="b")&&(check!="w"))
    {
        whid.push_back(QPoint(i,j));
        whi.removeOne(QPoint(i,j));
    }

    int deltaX = i-i0;
    int deltaY = j-j0;

    for (int l=1;l<=abs(deltaX)-1;l++)
    {
        if(s=="black")
        {
            for(int g=0;g<whi.size();g++)
            {
                if(whi[g]==QPoint(i0+l*abs(deltaX)/deltaX,j0+l*abs(deltaY)/deltaY))
                {
                    whi.removeAt(g);
                }
            }
        }
        if(s=="white")
        {
            for(int g=0;g<bla.size();g++)

            {
                if(bla[g]==QPoint(i0+l*abs(deltaX)/deltaX,j0+l*abs(deltaY)/deltaY))

                {
                    bla.removeAt(g);
                }
            }
        }
        if(s=="black+")
        {
            for(int g=0;g<whid.size();g++)
            {
                if(whid[g]==QPoint(i0+l*abs(deltaX)/deltaX,j0+l*abs(deltaY)/deltaY))
                {
                    whid.removeAt(g);
                }
            }
        }
        if(s=="white+")
        {
            for(int g=0;g<blad.size();g++)

            {
                if(blad[g]==QPoint(i0+l*abs(deltaX)/deltaX,j0+l*abs(deltaY)/deltaY))

                {
                    blad.removeAt(g);
                }
            }
        }
    }
    check="";
    s="";

    // treba byde zrobyty perevirky sho zrobyly hid

    networkAccessManager->turn(whi,bla,whid,blad); // viklikae func turn, pislya hody my kajemo servery sho pishly i server mae vidislaty novi coordinaty

    update();
}

void Widget::onclientTurn(const QList<QPoint> &wh, const QList<QPoint> &bl, const QList<QPoint> &whd, const QList<QPoint> &bld)
{
   whi = wh ;     // z TranferData vstavlaemo massiv dlya shashok
   bla = bl;      //
   whid = whd;    //
   blad = bld;    //
    update();
}
void Widget::onmyconnected()
{
    QMessageBox::information(this, "info", "poihaly!");
}

void Widget::onmydisconnected()
{
    QMessageBox::information(this, "info", "DOPOBACHENNYA");
    //close();
    qApp->closeAllWindows(); // zakrivae vse vikna
}
//void Widget::onServerTurn(const QList<QPoint> &wh, const QList<QPoint> &bl, const QList<QPoint> &whd, const QList<QPoint> &bld){}

