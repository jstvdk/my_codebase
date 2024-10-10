#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>
#include <QtGui>
#include <QtWidgets>
#include "serverch.h"

const int n = 10;
class Widget : public QWidget
{
    Q_OBJECT

public:
    Widget(QWidget *parent = 0);
    ~Widget();
protected:

    ServerCh *networkAccessManager;

    QList<QPoint> whi, bla;
    QList<QPoint> whid,blad;

    virtual void paintEvent(QPaintEvent *pe);
    virtual void mouseMoveEvent(QMouseEvent *mme);
    virtual void mouseReleaseEvent(QMouseEvent *mre); // hid zdijsnyetsa v mouserealease
    virtual void mousePressEvent(QMouseEvent *mpe);

    QPoint point0;
    QPoint point1;
    QPoint point3;
    QPoint delta;

    QString s;

public slots:
    // bydyt pruimaty signaly vid servera
    void onclientTurn(const QList<QPoint>&wh, const QList<QPoint>&bl, const QList<QPoint>&whd, const QList<QPoint>&bld);
    void onmyconnected();
    void onmydisconnected();

};

#endif // WIDGET_H

