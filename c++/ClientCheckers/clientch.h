#ifndef SERVERCH_H
#define SERVERCH_H

#include <QObject>
#include <QWidget>
#include <QtGui>
#include <QtWidgets>
#include <QtNetwork>
#include <string>

using namespace std;


class ClientCh : public QObject
{
    Q_OBJECT

protected:
    //QTcpServer *ClServer;
    //QTcpSocket *ClSocket;
    QTcpSocket *socket;
    QByteArray mes = 0;

public:
    explicit ClientCh(QString IP, QObject *parent = nullptr);
   ~ClientCh();

    void turn(const QList<QPoint>&whi,const QList<QPoint>&bla,const QList<QPoint>&whid,const QList<QPoint>&blad);
    //void SerTurn(const QList<QPoint>&whi,const QList<QPoint>&bla,const QList<QPoint>&whid,const QList<QPoint>&blad);

public slots:

    void onDisconnected();
    void onConnected();
    void transferData();
   // void transferDataServer();
   // void onConnect();

signals:
    void ServerTurn(const QList<QPoint>&wh,const QList<QPoint>&bl,const QList<QPoint>&whd,const QList<QPoint>&bld);
    void myconnected();
    void mydisconnected();
    //void ClientTurn(const QList<QPoint>&wh,const QList<QPoint>&bl,const QList<QPoint>&whd,const QList<QPoint>&bld);
};


#endif // CLIENTCH_H
