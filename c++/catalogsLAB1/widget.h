#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>
#include <string>
#include <QString>
#include <QtWidgets>
#include <iostream>
#include <QtGui>
#include "star.h"
#include <QVector>

using namespace std;

class Widget : public QWidget
{
    Q_OBJECT

protected:
    QPushButton *Spec;
    QPushButton *Mag;
    QPushButton *Load;
    QTextEdit *text;
    string Buffer;
    QVector <Star*> sstars;
//    QVector <Star> sstars;


public:
    Widget(QWidget *parent = 0);
    ~Widget();

public slots:
    void onSpec();
    void onMag();
    void onLoadFile();


};

#endif // WIDGET_H
