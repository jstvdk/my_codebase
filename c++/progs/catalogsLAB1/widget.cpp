#include "widget.h"
#include "star.h"
#include <iostream>
#include <QWidget>
#include <QObject>



using namespace std;

Widget::Widget(QWidget *parent)
    : QWidget(parent)
{
    resize(400,400);

    QVBoxLayout *vbl = new QVBoxLayout;
    QHBoxLayout *hbl = new QHBoxLayout;

    Spec = new QPushButton("dependence on the spectral class");
    Mag = new QPushButton("dependence on the magnitude");
    Load = new QPushButton("load catalogue into it");
    text = new QTextEdit;

    vbl -> addWidget(Load);
    vbl -> addWidget(Spec);
    vbl -> addWidget(Mag);
    hbl -> addLayout(vbl);
    hbl -> addWidget(text);

    this -> setLayout(hbl);

    connect(Spec,SIGNAL(clicked(bool)),SLOT(onSpec()));
    connect(Mag,SIGNAL(clicked(bool)),SLOT(onMag()));
    connect(Load,SIGNAL(clicked(bool)),SLOT(onLoadFile()));
}

Widget::~Widget()
{


}

void Widget::onSpec()
{

        text -> setText("23");
}

void Widget::onMag()
{
    text -> setText("2");
}

void Widget::onLoadFile()
{
    Star *ss = new Star;
    ifstream in; in.open("/home/jstvdk/data/ppm1.txt");

     if(!in)
       text -> setText("load failed");
     int i = 0;
     while(in)
     {
         getline(in,Buffer);
                 if(Buffer.length()<1)
                 break;


                            string formag = Buffer.substr(19,4);
                            double mag = atof(formag.c_str());

                            string forspec = Buffer.substr(24,2);

                            ss->setMag(mag);
                            ss->setSpec(forspec);

                            sstars.push_back(ss);
        i++;


//        qDebug() << "spectral class of " << i << "star - " << ss->getSpec().c_str();
//        qDebug() << "magnitude of " << i << "star - " << ss->getMag();
//        //qDebug() << sstars[i].getSpec().c_str();
//        qDebug() << sstars;
     }


     text -> setText("loaded successfully");

//     for (int i = 0; i < sstars.size(); i++)
//     {
//         qDebug() << sstars[i];
//     }
                                 delete ss;
}
