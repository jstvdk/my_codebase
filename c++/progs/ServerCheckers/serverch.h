#ifndef SERVERCH_H
#define SERVERCH_H

#include <QObject>
#include <QWidget>
#include <QtGui>
#include <QtWidgets>
#include <QtNetwork>

class ServerCh : public QObject
{
    Q_OBJECT
public:

    bool isConnect() { return socket != 0; };
    void turn(const QList<QPoint>&whi, const QList<QPoint>&bla, const QList<QPoint>&whid, const QList<QPoint>&blad);
    // turn byde viklikatus widgetom koly gravez zrobyv hid

    explicit ServerCh(QObject *parent = nullptr);
    ~ServerCh();

signals:
    //  если мы подключим сигнал к слоту, слот будет вызван с параметрами сигнала в нужное время.
    void clientTurn(const QList<QPoint>&wh, const QList<QPoint>&bl, const QList<QPoint>&whd, const QList<QPoint>&bld); // vyklykae connect v Widget.cpp
    void myconnected(); // signal generyetsa koly proishlo ziednannya i bylu z4utanni dani, todi vyklykaetsa connect v Widget.cpp
    void mydisconnected(); // signal generyetsa koly socket vidkly4ivsa, todi vyklykaetsa connect v Widget.cpp

public slots:

    void onConnect(); // byde viklikatus koly client postykae servery i potim posilaty signal
    void onDisconnect();
    void transferData(); // QTCP socket poshle ReadyRead i byde viklikatus cya func
    //void transferDataClient();
protected:

    QTcpServer *server;
    QTcpSocket *socket;
   // QTcpSocket *SSocket;
    QByteArray mes = 0;
};

#endif // SERVERCH_H
// qtcpserver - запускається і сидить чекає коли хтось постукає, функція лісн цим займається,
// коли кліент стукає то створюємо сокет, (некст пендінг конекшн), а два сокета можуть вже передавати дані
// сигнал конектед якщо хтось приєднався, якщо приймаємо дані то генерується сигнал кліенттьорн
//
