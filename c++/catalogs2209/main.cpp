#include <iostream>
#include <star.h>
#include <cmath>
#include <fstream>

const int arrsize = 3;

using namespace std;

double dtrmnnt(double a[arrsize][arrsize+1]);
double Holetsky(double a[][arrsize]);
double matrxminor(double a[arrsize][arrsize], int i, int j);
double **reverse(double a[arrsize][arrsize]);
void freematrx(double **p, int arrsize);

int main(int argc, char *argv[])
{
    const int N = 400000;

    bool checkinfo = false;

    Star *stars = new Star[N];
    string Buffer;

    int i = 0;
    int j,o;
    char ch = 'Z';

    double coef[arrsize + 1];
    double matrx[arrsize][arrsize + 1];
    double matrxA[arrsize][arrsize];

//    const string cat[2] = {"/home/jstvdk/data/ppm1.txt","/home/jstvdk/data/ppm2.txt"};
//    cout << cat[0] << "   " << cat[1] << endl;



    ifstream in;    in.open("/home/jstvdk/data/ppm1.txt");

                    while(in)
                    {
                     getline(in, Buffer);
                     if (Buffer.length() < 1)
                         break;

                            if ( argc > 1)
                            {
                                checkinfo = true;
                                string leng = argv[1];
                                const char mag = argv[2][0];
                                    if ( leng.size() == 1)
                                    {
                                        string forbuf = Buffer.substr(24,1);
                                        const char *Buf = forbuf.c_str();
                                            if ( argc > 1 && *Buf != argv[1][0])
                                                continue;
//                                                    if ( i%10 == 0)
//                                                    {
//                                                        cout << "forbuf - " << i << " = " << forbuf << endl;
//                                                    }
                                    }
                                    else
                                    {
                                        string forspec = Buffer.substr(24,2);
                                            if ( argc > 1 && forspec != argv[1])
                                                continue;
                                                    if ( i%10 == 0)
                                                    {
                                                        cout << "forbuf - " << i << " = " << forspec << endl;
                                                    }
                                    }
                            }
                            if ( argc == 5)
                            {
                                string formag = Buffer.substr(19,2);
                                cout << formag << endl;
                                if ( formag != argv[4])
                                    continue;
                            }

                            string forah = Buffer.substr(27, 2); // Right Ascention hours
                            int ah = atoi(forah.c_str());

                            string foram = Buffer.substr(30, 2);
                            int am = atoi(foram.c_str());

                            string foras = Buffer.substr(33, 8);
                            double as = atof(foras.c_str());

                            double alpha = (ah+(am+as/60)/60)*15*(M_PI/180);  // alpha in rad

                            char signA = Buffer.at(41);

                            string fordd = Buffer.substr(42, 3); // Declination hours
                            int dd = atoi(fordd.c_str());

                 if (signA == '-')
                 {
                     dd = -dd;
                 }

                            string fordm = Buffer.substr(45, 2);
                            int dm = atoi(fordm.c_str());

                            string fords = Buffer.substr(48, 5);
                            double ds = atof(fords.c_str());

                            double delta = (dd+(dm+ds/60)/60)*(M_PI/180); // delta in rad


                            string forma = Buffer.substr(55, 6);
                            double ma = atof(forma.c_str()) * 15;   // Proper motion in RA ,  * 15 bo v secyndah 4asy, perevodumo v secundy dugy

                            string formd = Buffer.substr(63, 6);
                            double md = atof(formd.c_str());  // Proper motion in DE

//                 cout << i+1 << "  RA hours = " << ah << " minutes = " << am << " seconds " << as << endl;
//                 cout << i+1 << " DEC hours = " << dd << " minutes = " << dm << " seconds " << ds << " sign = " << signA << endl;
//                 cout << "alpha = " << alpha << "  delta = " << delta << " ma = " << ma << " md = " << md << endl;

//                 out << alpha << "  " << delta << "  " << ma << "  " << md << endl;

                                     stars[i].setRA(alpha);
                                     stars[i].setdec(delta);
                                     stars[i].setmRA(ma);
                                     stars[i].setmdec(md);

                                     double p = cos(stars[i].getRA())*sin(stars[i].getdec());
                                     double q = sin(stars[i].getdec())*sin(stars[i].getRA());
                                     double s = cos(stars[i].getdec());
                                     double t = sin(stars[i].getRA());
                                     double u = cos(stars[i].getRA());
                                     double forz = 0;

                                                 coef[0] = (-p);
                                                 coef[1] = (-q);
                                                 coef[2] = s;
                                                 coef[3] = stars[i].getmdec();

                 for(o = 0; o < 3; ++o)   // 1 matrix
                 {
                     for (j = 0; j < 4; ++j)
                         matrx[o][j] += coef[o] * coef[j];
                 }

                                                 coef[0] = (-t);
                                                 coef[1] = u;
                                                 coef[2] = forz;
                                                 coef[3] = stars[i].getmRA()*cos(stars[i].getdec());

                 for(o = 0; o < 3; ++o)   // 2 matrix
                 {
                     for (j = 0; j < 4; ++j)
                         matrx[o][j] += coef[o] * coef[j];
                 }
             ++i;

                 //cout << "forbuf - " << i << " = " << forbuf << endl;
             }

    in.close();
//
//
//
//
//
//
//
    ifstream bin;    bin.open("/home/jstvdk/data/ppm2.txt");
                                                                    i = 0;
                     while(bin)
                          {
                              getline(bin, Buffer);
                              if (Buffer.length() < 1)
                                  break;

                              if ( argc > 1)
                              {
                                  string leng = argv[1];
                                      if ( leng.size() == 1)
                                      {
                                          string forbuf = Buffer.substr(24,1);
                                          const char *Buf = forbuf.c_str();
                                              if ( argc > 1 && *Buf != argv[1][0])
                                                  continue;
//                                                      if ( i%10 == 0)
//                                                      {
//                                                          cout << "forbuf - " << i << " = " << forbuf << endl;
//                                                      }
                                      }
                                      else
                                      {
                                          string forspec = Buffer.substr(24,2);
                                              if ( argc > 1 && forspec != argv[1])
                                                  continue;
                                                      if ( i%10 == 0)
                                                      {
                                                          cout << "forbuf - " << i << " = " << forspec << endl;
                                                      }
                                      }
                              }
                              if ( argc == 5)
                              {
                                  string formag = Buffer.substr(19,2);
                                  if ( formag != argv[4])
                                      continue;
                              }


                                     string forah = Buffer.substr(27, 2); // Right Ascention hours
                                     int ah = atoi(forah.c_str());

                                     string foram = Buffer.substr(30, 2);
                                     int am = atoi(foram.c_str());

                                     string foras = Buffer.substr(33, 8);
                                     double as = atof(foras.c_str());

                                     double alpha = (ah+(am+as/60)/60)*15*(M_PI/180);  // alpha in rad

                                     char signA = Buffer.at(41);

                                     string fordd = Buffer.substr(42, 3); // Declination hours
                                     int dd = atoi(fordd.c_str());

                          if (signA == '-')
                          {
                              dd = -dd;
                          }

                                     string fordm = Buffer.substr(45, 2);
                                     int dm = atoi(fordm.c_str());

                                     string fords = Buffer.substr(48, 5);
                                     double ds = atof(fords.c_str());

                                     double delta = (dd+(dm+ds/60)/60)*(M_PI/180); // delta in rad

                                     string forma = Buffer.substr(55, 6);
                                     double ma =(atof(forma.c_str())) * 15;   // Proper motion in RA

                                     string formd = Buffer.substr(63, 6);
                                     double md = atof(formd.c_str());  // Proper motion in DE

//                          cout << i+1 << "  RA hours = " << ah << " minutes = " << am << " seconds " << as << endl;
//                          cout << i+1 << " DEC hours = " << dd << " minutes = " << dm << " seconds " << ds << " sign = " << signA << endl;
//                          cout << "alpha = " << alpha << "  delta = " << delta << " ma = " << ma << " md = " << md << endl;
//                          out << alpha << "  " << delta << "  " << ma << "  " << md << endl;

                                              stars[i].setRA(alpha);
                                              stars[i].setdec(delta);
                                              stars[i].setmRA(ma);
                                              stars[i].setmdec(md);

                                              double p = cos(stars[i].getRA())*sin(stars[i].getdec());
                                              double q = sin(stars[i].getdec())*sin(stars[i].getRA());
                                              double s = cos(stars[i].getdec());
                                              double t = sin(stars[i].getRA());
                                              double u = cos(stars[i].getRA());
                                              double forz = 0;

                                                          coef[0] = (-p);
                                                          coef[1] = (-q);
                                                          coef[2] = s;
                                                          coef[3] = stars[i].getmdec();

                          for(o = 0; o < 3; ++o)   // 1 matrix
                          {
                              for (j = 0; j < 4; ++j)
                                  matrx[o][j] += coef[o] * coef[j];
                          }

                                                          coef[0] = (-t);
                                                          coef[1] = u;
                                                          coef[2] = forz;
                                                          coef[3] = stars[i].getmRA()*cos(stars[i].getdec());

                          for(o = 0; o < 3; ++o)   // 2 matrix
                          {
                              for (j = 0; j < 4; ++j)
                                  matrx[o][j] += coef[o] * coef[j];

//                              cout << "z = " << coef[2] << endl;
                          }
                      ++i;

//                          cout << "forbuf - " << i << " = " << forbuf << endl;
                      }

    bin.close();

    {
//
//
//
//
//
//    for(o = 0; o < 3; ++o) // output matrix A
//    {
//        cout << "\n";
//        for (j = 0; j < 4; ++j)
//            cout << matrx[o][j] << " ";
//    }
//
//                         double det = 0;
//                         det = matrx[0][0]*matrx[1][1]*matrx[2][2] + matrx[0][1]*matrx[1][2]*matrx[2][0] + matrx[0][2]*matrx[1][0]*matrx[2][1]
//                             - matrx[0][2]*matrx[1][1]*matrx[2][0] - matrx[0][0]*matrx[1][2]*matrx[2][1] - matrx[0][1]*matrx[1][0]*matrx[2][2];
//
//    cout << "\n determinant = " << det << endl;
//
//    for (i =0; i < 3; ++i)
//    {
//        for (j=0; j<4; ++j)
//        {
//            cout << "matrx[" << i << "]" << "[" << j << "] = " << matrx[i][j];
//            cout << "\n";
//        }
//    }
//
//    cout << "\n\n";
//    for (int i = 0; i < 3; ++i) // output matrix B
//    {
//        int j = 3;
//        cout << matrx[i][j] << endl;
//    }
//
//                                                    double dtr = dtrmnnt(matrx);
//    cout << "\n calculated determinant by function = " << dtr << endl;
//
//    cout << stars[181730].getRA() << endl;
//     double *q = Holetsky(matrx);
//    cout << "\n" << *(q+0) << "  " << *(q+1) << "  " << *(q+2) << endl;
//
    }

//
//
//
//
//
//          Holetsky
    {

//                double l[6];
//                double y[3];
//                double x[3];

//                l[0] = sqrt(matrx[0][0]); // l11 -> l11
//                l[1] = matrx[1][0] / l[0]; // l21 -> l12
//                l[2] = matrx[2][0] / l[0]; // l31 -> l13
//                l[3] = sqrt(matrx[1][1] - (l[1] * l[1])); // l22 -> l22
//                l[4] = matrx[2][1] - l[2] * l[1]; // l32 -> l23
//                l[5] = sqrt(matrx[1][1] - l[3] * l[3] - l[4] * l[4]); // l33

//    for (int i(0); i<6; ++i)
//    {
//        cout << l[i] << "  ";
//    }
//    cout << "\n";

//                y[0] = matrx[0][3] / l[0];
//                y[1] = (matrx[1][3] - l[1] * y[0]) / l[3];
//                y[2] = (matrx[2][3] - (l[2] * y[0]) - (l[4] * y[1])) / l[5];

//    for (int i(0); i<3; ++i)
//    {
//        cout << y[i] << "  ";
//    }
//    cout << "\n";

//                x[0] = y[2] / l[5];
//                x[1] = (y[1] - (l[4] * x[0])) / l[3];
//                x[2] = (y[0] - (l[1] * x[2]) - (l[2] * x[0])) / l[0];

//    for (int i(0); i<3; ++i)
//    {
//        cout << x[i] << "  ";
//    }
    }

//
//
//
//
//          Kramer


                                                        double matrxbaa[3][4];
                                                        double matrxaba[3][4];
                                                        double matrxaab[3][4];

    for (i = 0; i < 3; ++i)
    {
        for ( j = 0; j < 3 ; ++j)
        {
          if (j == 0)
              matrxbaa[i][j] = matrx[i][3];
          else
              matrxbaa[i][j] = matrx[i][j];
        }
    }

    for (i = 0; i < 3; ++i)
    {
        for (j = 0;j<3;++j)
        {
            if (j==1)
                matrxaba[i][j] = matrx[i][3];
            else
                matrxaba[i][j] = matrx[i][j];
        }
    }

    for (i = 0; i < 3; ++i)
    {
        for (j = 0;j<3;++j)
        {
            if (j==2)
                matrxaab[i][j] = matrx[i][3];
            else
                matrxaab[i][j] = matrx[i][j];
        }
    }

//    for (o = 0; o < 3; ++o) // output matrix baa
//    {
//        cout << "\n";
//        for (j = 0; j < 3; ++j)
//        {
//            cout << matrxbaa[o][j] << " ";
//        }
//    }
//                                                cout << "\n\n";
//    for (o = 0; o < 3; ++o) // output matrix aba
//    {
//        cout << "\n";
//        for (j = 0; j < 3; ++j)
//        {
//            cout << matrxaba[o][j] << " ";
//        }
//    }
//                                                cout << "\n\n";
//    for (o = 0; o < 3; ++o) // output matrix aab
//    {
//        cout << "\n";
//        for (j = 0; j < 3; ++j)
//        {
//            cout << matrxaab[o][j] << " ";
//        }
//    }

                                                        double xxx = dtrmnnt(matrxbaa) / dtrmnnt(matrx);
                                                        double yyy = dtrmnnt(matrxaba) / dtrmnnt(matrx);
                                                        double zzz = dtrmnnt(matrxaab) / dtrmnnt(matrx);

    cout << "___________________RESULTS: " << endl;
    cout << "\n x = " << xxx << "      y = " << yyy << "      z = " << zzz << endl;
    cout << "\n";

    double RAforApex = atan2(yyy,xxx);
    double DeltaforApex = atan2(zzz,sqrt(xxx*xxx + yyy*yyy));

    double RAA = 360 - RAforApex*(180/M_PI);
    double DeltaA = -(DeltaforApex*(180/M_PI));

    cout << " RA for Apex = " << RAA << "          Delta for Apex = " << DeltaA << endl;

//
//
//
//
// reverse matrx calculating

    for (int o = 0; o < arrsize; ++o)
    {
        for ( int w = 0; w < arrsize; ++w)
        {
            matrxA[o][w] = matrx[o][w];
        }
    }

    double **revmatrx = (double **)malloc(arrsize * (sizeof(double *)));
    for ( int i = 0; i < arrsize; ++i)
    {
        revmatrx[i] = (double *)malloc(arrsize * (sizeof(double *)));
    }

    revmatrx = reverse(matrxA);

//    for (int o = 0; o < arrsize; ++o)   // output reverse matrix
//    {
//        cout << endl;
//        for ( int w = 0; w < arrsize; ++w)
//        {
//            cout << " " << revmatrx[o][w] << " ";
//        }
//    }


                                    double sigmaX = sqrt(revmatrx[0][0]);
                                    double sigmaY = sqrt(revmatrx[1][1]);
                                    double sigmaZ = sqrt(revmatrx[2][2]);

        cout << "\n sigma x = " << sigmaX << "\n sigma y = " << sigmaY << "\n sigma z = " << sigmaZ << endl;

        if ( argc > 2 )  // correlation coef
        {
            string forii = argv[2];
            string forjj = argv[3];
            int ii = atoi(forii.c_str());
            int jj = atoi(forjj.c_str());
            //cout << "ii = " << ii << " jj = " << jj << endl;
            double ro = revmatrx[ii][jj] / sqrt(revmatrx[ii][ii] * revmatrx[jj][jj]);
            cout << "\n correlation coefficient for index [" << ii << "][" << jj << "] = " << ro << endl;
        }

        if (checkinfo)
        {
            cout << "\n This was calculated for " << argv[1] << " spectral class" << endl;
            if ( argc == 5 )
            {
                cout << " and for " << argv[4] << " magnitude" << endl;
            }
        }

        else
        {
            cout << "\n This was calculated for all spectral classes from North and South ppm1 catalog" << endl;
        }
    cout << "\n\n\n\n\n\n";

    for ( int i = 0; i < argc; ++ i)
    {
        cout << "arg number " << i << " = " << argv[i] << endl;
    }
    cout << "argc = " << argc << endl;


    // output to file
    //ofstream out; out.open("/home/jstvdk/data/ppmdata.txt", ios_base::app);

    //out << "Right Ascension = " <<RAA << " Delta = " <<0 Delta >> " " ;

    freematrx(revmatrx, arrsize);
    delete[] stars;

    return 0;
}

double dtrmnnt(double a[arrsize][arrsize+1])
{
    double temp;
    temp = a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1] -
           a[0][2]*a[1][1]*a[2][0] - a[0][0]*a[1][2]*a[2][1] - a[0][1]*a[1][0]*a[2][2];
    return temp;
}

double Holetsky(double a[][arrsize])
{
    double antierror = a[0][0];
    /*double* l = new double[5];
    //double* y = new double[2];
    //
    //double x1,x2,x3;

    *(l+0) = sqrt(a[0][0]); // l11 -> l11
   *(l+1) = a[1][0] / *(l+0); // l21 -> l12
   *(l+2) = a[2][0] / *(l+0); // l31 -> l13
   *(l+3) = sqrt(a[1][1] - (*(l+1) * *(l+1))); // l22 -> l22
   *(l+4) = a[2][1] - (*(l+2) * *(l+1)); // l32 -> l23
   *(l+5) = sqrt(a[1][1] - (*(l+2) * *(l+2)) - (*(l+4) * *(l+4))); // l33

    *(y+0) = a[0][3] / (*(l+0));
    *(y+1) = (a[1][3] - (*(l+1) * *(y+0))) / *(l+3);
    *(y+2) = (a[2][3] - (*(l+2) * *(y+0)) - (*(l+4) * *(y+1))) / *(l+5);

    x3 = *(y+2) / *(l+5);
    x2 = (*(y+1) - (*(l+4) * x3)) / *(l+3);
    x1 = (*(y+0) - (*(l+1) * x2) - (*(l+2) * x3)) / *(l+0);

    //delete[] y;
    //delete[] l;
    return x;*/
    return antierror;
}

void freematrx(double **p, int size)
{
    for ( int i = 0; i < size; ++i)
    {
        free(p[i]);
        *p[i] = NULL;
    }
    free(p);
        *p = NULL;
}

double matrxminor(double a[arrsize][arrsize], int i, int j)
{
//    double temparr[3][3];
    double temparrformin[2][2];

    int bcoef[2];
    int kcoef[2];

//    for (int o = 0; o < 3; ++o)
//    {
//        if ( o == i)
//        {
//            for ( int w = 0; w < 3; ++w)
//                temparr[o][w] = 0;
//        }
//        else
//            for ( int k = 0; k < 3; ++k)
//            {
//                if ( k == j)
//                {
//                    for ( int e = 0; e < 3; ++e)
//                        temparr[e][k] = 0;
//                }
//                else
//                    temparr[o][k] = a[o][k];
//            }
//    }

            if ( i == 0 ) { bcoef[0] = 1; bcoef[1] = 2; }
            if ( i == 1 ) { bcoef[0] = 0; bcoef[1] = 2; }
            if ( i == 2 ) { bcoef[0] = 0; bcoef[1] = 1; }

            if ( j == 0 ) { kcoef[0] = 1; kcoef[1] = 2; }
            if ( j == 1 ) { kcoef[0] = 0; kcoef[1] = 2; }
            if ( j == 2 ) { kcoef[0] = 0; kcoef[1] = 1; }

    for (int o = 0; o < 2; ++o)
    {
        for (int k = 0; k < 2; ++k)
        {
            temparrformin[o][k] = a[bcoef[o]][kcoef[k]];
        }
    }

    double tempdet = temparrformin[0][0] * temparrformin[1][1] -   temparrformin[0][1] * temparrformin[1][0];
    return tempdet;
}

double **reverse(double a[arrsize][arrsize])
{
    const int N = 3;
    double matrx[arrsize][arrsize];
    double minormatrix[arrsize][arrsize];
    double algebraicmtrx[arrsize][arrsize];
    double additionmtrx[arrsize][arrsize];
    double detmtrx;

    for (int i = 0; i < N; ++i)
    {
          for ( int j = 0; j < N; ++j)
           {
                matrx[i][j] = a[i][j];
           }
    }

    for ( int i = 0; i < N; ++i)
    {
//        cout << endl;
        for (int j = 0; j < N; ++j)
        {
            minormatrix[i][j] = matrxminor(matrx, i, j);
//            cout << " " << minormatrix[i][j];
        }
    }

//    cout << "\n\n matrix of algebraic supplement ->" << endl;

    for (int i = 0; i < N; ++i)
    {
//        cout << endl;
        for ( int j = 0; j < N; ++j)
        {
            algebraicmtrx[i][j] = pow(-1,i+j) * minormatrix[i][j];
//            cout << " " << algebraicmtrx[i][j];
        }
    }

//    cout << "\n\n transponated matrix ->" << endl;

    for ( int i = 0; i < N; ++i)
    {
//        cout << "\n";
        for ( int j = 0; j < N; ++j)
        {
            additionmtrx[i][j] = algebraicmtrx[j][i];
//            cout << " " << additionmtrx[i][j];
        }
    }

    detmtrx = matrx[0][0]*matrx[1][1]*matrx[2][2] + matrx[0][1]*matrx[1][2]*matrx[2][0] + matrx[0][2]*matrx[1][0]*matrx[2][1]
            - matrx[0][2]*matrx[1][1]*matrx[2][0] - matrx[0][0]*matrx[1][2]*matrx[2][1] - matrx[0][1]*matrx[1][0]*matrx[2][2];
//    cout << "det  = " << detmtrx;

        double **p = (double **)malloc(N * sizeof(double *));
        for ( int i = 0; i < N; ++i)
        {
            p[i] = (double *)malloc(N * sizeof(double *));
        }

        for ( int i = 0; i < N; ++i)
        {
//            cout << "\n";
            for ( int j = 0; j < N; ++j)
        {
            p[i][j] = additionmtrx[i][j] / detmtrx;
//            cout << " " << p[i][j];
        }
    }
    return p;
}
