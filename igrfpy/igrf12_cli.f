      SUBROUTINE IGRF12(ITYPE,DATE,ALT,IFL,
     1                  XLTI,XLTF,XLTD,XLNI,XLNF,XLND,
     2                   aLat,aLon,aD,aS,aH,aX,aY,aZ,aF,
     3                   totpts)
! C
! C     This is a program for synthesising geomagnetic field values from the 
! C     International Geomagnetic Reference Field series of models as agreed
! c     in December 2014 by IAGA Working Group V-MOD. 
! C     It is the 12th generation IGRF, ie the 11th revision. 
! C     The main-field models for 1900.0, 1905.0,..1940.0 and 2015.0 are 
! C     non-definitive, those for 1945.0, 1950.0,...2010.0 are definitive and
! C     the secular-variation model for 2015.0 to 2020.0 is non-definitive.
! C
! C     Main-field models are to degree and order 10 (ie 120 coefficients)
! C     for 1900.0-1995.0 and to 13 (ie 195 coefficients) for 2000.0 onwards. 
! C     The predictive secular-variation model is to degree and order 8 (ie 80
! C     coefficients).
! C
! C     Options include values at different locations at different
! C     times (spot), values at same location at one year intervals
! C     (time series), grid of values at one time (grid); geodetic or
! C     geocentric coordinates, latitude & longitude entered as decimal
! C     degrees or degrees & minutes (not in grid), choice of main field 
! C     or secular variation or both (grid only).
! C Recent history of code:
! c     Aug 2003: 
! c     Adapted from 8th generation version to include new maximum degree for
! c     main-field models for 2000.0 and onwards and use WGS84 spheroid instead
! c     of International Astronomical Union 1966 spheroid as recommended by IAGA
! c     in July 2003. Reference radius remains as 6371.2 km - it is NOT the mean
! c     radius (= 6371.0 km) but 6371.2 km is what is used in determining the
! c     coefficients. 
! c     Dec 2004: 
! c     Adapted for 10th generation
! c     Jul 2005: 
! c     1995.0 coefficients as published in igrf9coeffs.xls and igrf10coeffs.xls
! c     now used in code - (Kimmo Korhonen spotted 1 nT difference in 11 coefficients)
! c     Dec 2009:
! c     Adapted for 11th generation
! c     Dec 2014:
! c     Adapted for 12th generation
! c
! C ******************************************************************************
! C Edits to enable F2PY compiling (to use with Python)
! C Liam Kilcommons Sept. 2018 following IGRF11.f90 by Sebastien - Sept. 2012
! C
! C
! C Edits to switch IGRF to subroutine
! C   INPUTS:
! C       - ITYPE:
! C           - 1 - geodetic (shape of Earth is approximated by a spheroid)
! C           - 2 - geocentric (shape of Earth is approximated by a sphere)
! C       - DATE: date in years A.D. (ignored if IOPT=2)
! C       - ALT: altitude or radial distance in km (depending on ITYPE)
! C       - XLTI,XLTF,XLTD: latitude (initial, final, increment) in decimal degrees
! C       - XLNI,XLNF,XLND: longitude (initial, final, increment) in decimal degrees
! C       - IFL: value for MF/SV flag:
! C           - 0 for main field (MF)
! C           - 1 for secular variation (SV)
! C           - 2 for both
! C   OUTPUTS:
! C       - aLat is the latitude of each point
! C       - aLon is the longitude of each point
! C       - D is declination in degrees (+ve east)
! C       - I is inclination in degrees (+ve down)
! C       - H is horizontal intensity in nT
! C       - X is north component in nT
! C       - Y is east component in nT
! C       - Z is vertical component in nT (+ve down)
! C       - F is total intensity in nT
! C
! C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
      CHARACTER*1 IA
      CHARACTER*11 TYPE
      CHARACTER*20 NAME
      CHARACTER*30 FNM
      integer totpts
      INTEGER NPTS                                                              ! Edit LMK following SdL
      integer ITYPE,IFL                                                         ! Edit LMK following SdL
      real date                                                                 ! Edit LMK following SdL
      real*8 ALT                                                                ! Edit LMK following SdL
      real*8 XLTI,XLTF,XLTD                                                     ! Edit LMK following SdL
      real*8 XLNI,XLNF,XLND                                                     ! Edit LMK following SdL
      real*8,DIMENSION(totpts) :: aLat,aLon                                     ! Edit LMK following SdL
      real*8,DIMENSION(totpts) :: aD,aS,aH                                      ! Edit LMK following SdL
      real*8,DIMENSION(totpts) :: aX,aY,aZ,aF                                   ! Edit LMK following SdL
Cf2py intent(in) ITYPE,IFL,DATE,ALT
Cf2py intent(in) XLTI,XLTF,XLTD
Cf2py intent(in) XLNI,XLNF,XLND
Cf2py integer intent(hide),depend(XLTI,XLTF,XLTD,XLNI,XLNF,XLND) :: totpts=(abs(XLTF-XLTI)/XLTD+1)*(abs(XLNF-XLNI)/XLND+1)
Cf2py intent(out),depend(totpts) :: aLat,aLon,aD,aS,aH,aX,aY,aZ,aF
      DATA DTMN,DTMX/1900.0,2025.0/
C
C
!     WRITE(6,*)
!     WRITE(6,*)'******************************************************'
!     WRITE(6,*)'*              IGRF SYNTHESIS PROGRAM                *'
!     WRITE(6,*)'*                                                    *'
!     WRITE(6,*)'* A program for the computation of geomagnetic       *'
!     WRITE(6,*)'* field elements from the International Geomagnetic  *'
!     WRITE(6,*)'* Reference Field (12th generation) as revised in    *'
!     WRITE(6,*)'* December 2014 by the IAGA Working Group V-MOD.     *'
!     WRITE(6,*)'*                                                    *'
!     WRITE(6,*)'* It is valid for dates from 1900.0 to 2020.0,       *'
!     WRITE(6,*)'* values up to 2025.0 will be computed but with      *'
!     WRITE(6,*)'* reduced accuracy. Values for dates before 1945.0   *'
!     WRITE(6,*)'* and after 2010.0 are non-definitive, otherwise the *'
!     WRITE(6,*)'* values are definitive.                             *'
!     WRITE(6,*)'*                                                    *'
!     WRITE(6,*)'* Susan Macmillan          British Geological Survey *'
!     WRITE(6,*)'*                           IAGA Working Group V-MOD *'
!     WRITE(6,*)'******************************************************'
!     WRITE(6,*)
!     WRITE(6,*)'Enter name of output file (30 characters maximum)'
!     WRITE(6,*)'or press "Return" for output to screen'
!     READ (5,991) FNM
! 991 FORMAT (A30)
!     IF (ICHAR(FNM(1:1)).EQ.32) THEN
       IU = 6
!      ELSE
!       IU = 2
!       OPEN (UNIT = IU,FILE = FNM,STATUS = 'NEW')
!      END IF
      FACT = 180.0/3.141592654
      NCOUNT = 0
C
!   10 WRITE(6,*)'Enter value for coordinate system:'
!      WRITE(6,*)
!     1'1 - geodetic (shape of Earth is approximated by a spheroid)'
!      WRITE(6,*)
!     1'2 - geocentric (shape of Earth is approximated by a sphere)'
!      READ (5,*) ITYPE
      IF (ITYPE.LT.1.OR.ITYPE.GT.2) GO TO 208 ! LMK added new error
      IF (ITYPE.EQ.1) TYPE = ' geodetic  '
      IF (ITYPE.EQ.2) TYPE = ' geocentric'
C
!   20 WRITE(6,*) 'Choose an option:'
!      WRITE(6,*) '1 - values at one or more locations & dates'
!      WRITE(6,*) '2 - values at yearly intervals at one location'
!      WRITE(6,*) '3 - values on a latitude/longitude grid at one date'
!      READ (5,*) IOPT
!      IF(IOPT.LT.1.OR.IOPT.GT.3) GO TO 20
      IOPT=3 ! LMK default to grid 
      IF (IOPT.EQ.3) GO TO 150
C LMK This is output options 
!    30 WRITE(6,*)'Enter value for format of latitudes and longitudes:'
!       WRITE(6,*)'1 - in degrees & minutes'
!       WRITE(6,*)'2 - in decimal degrees'
!       READ (5,*) IDM
!       IF (IDM.LT.1.OR.IDM.GT.2) GO TO 30
!       IF (NCOUNT.EQ.0) GOTO 50
! C LMK Following is command line interface code up to label 150
!    40 WRITE(6,*) 
!      1'Do you want values for another date & position? (y/n)'
!       READ (5,'(A1)') IA    
!       IF (IA.NE.'Y'.AND.IA.NE.'y'.AND.IA.NE.'N'.AND.IA.NE.'n')
!      1     GO TO 40
!       IF(IA.EQ.'N'.OR.IA.EQ.'n') THEN
!        WRITE(IU,928)
!   928  FORMAT (' D is declination (+ve east)'/
!      1          ' I is inclination (+ve down)'/
!      2          ' H is horizontal intensity'/
!      3          ' X is north component'/
!      4          ' Y is east component'/
!      5          ' Z is vertical component (+ve down)'/
!      6          ' F is total intensity')
!        WRITE(IU,929)
!   929  FORMAT (/' SV is secular variation (annual rate of change)')
!        IF (ITYPE.EQ.2) THEN
!         WRITE(IU,*)
!      1'These elements are relative to the geocentric coordinate system'
!        ELSE
!         WRITE(IU,*)
!        ENDIF
!        STOP
!       ENDIF
! C
!    50 NCOUNT = 1
!       IF (IOPT.NE.2) THEN
!        WRITE(6,*) 'Enter date in years A.D.'
!        READ (5,*) DATE
!        IF (DATE.LT.DTMN.OR.DATE.GT.DTMX) GO TO 209
!       ENDIF

!       IF(ITYPE.EQ.1) THEN
!        WRITE(6,*) 'Enter altitude in km'
!       ELSE  
!        WRITE(6,*) 'Enter radial distance in km (>3485 km)'
!       END IF
!       READ (5,*) ALT
!       IF (ITYPE.EQ.2.AND.ALT.LE.3485.0) GO TO 210
! C
!       IF (IDM.EQ.1) THEN
!        WRITE(6,*) 'Enter latitude & longitude in degrees & minutes'
!        WRITE(6,*) '(if either latitude or longitude is between -1'
!        WRITE(6,*) 'and 0 degrees, enter the minutes as negative).'
!        WRITE(6,*) 'Enter 4 integers' 
!        READ (5,*) LTD,LTM,LND,LNM
!        IF (LTD.LT.-90.OR.LTD.GT.90.OR.LTM.LE.-60.OR.LTM.GE.60) GO TO 204
!        IF (LND.LT.-360.OR.LND.GT.360.OR.LNM.LE.-60.OR.LNM.GE.60)
!      1    GO TO 205
!        IF (LTM.LT.0.AND.LTD.NE.0) GO TO 204
!        IF (LNM.LT.0.AND.LND.NE.0) GO TO 205
!        CALL DMDDEC (LTD,LTM,XLT)
!        CALL DMDDEC (LND,LNM,XLN)
!       ELSE
!        WRITE(6,*) 'Enter latitude & longitude in decimal degrees'
!        READ (5,*) XLT,XLN
!        IF (XLT.LT.-90.0.OR.XLT.GT.90.0) GO TO 202
!        IF (XLN.LT.-360.0.OR.XLN.GT.360.0) GO TO 203
!       ENDIF
! C
!       WRITE(*,*) 'Enter place name (20 characters maximum)'
!       READ (*,'(A)') NAME
!       CLT = 90.0 - XLT
!       IF (CLT.LT.0.0.OR.CLT.GT.180.0) GO TO 204
!       IF (XLN.LE.-360.0.OR.XLN.GE.360.0) GO TO 205
!       IF (IOPT.EQ.2) GOTO 60
! C
!       CALL IGRF12SYN (0,DATE,ITYPE,ALT,CLT,XLN,X,Y,Z,F)
!       D = FACT*ATAN2(Y,X)
!       H = SQRT(X*X + Y*Y)
!       S = FACT*ATAN2(Z,H)
!       CALL DDECDM (D,IDEC,IDECM)
!       CALL DDECDM (S,INC,INCM)
! C
!       CALL IGRF12SYN (1,DATE,ITYPE,ALT,CLT,XLN,DX,DY,DZ,F1)
!       DD = (60.0*FACT*(X*DY - Y*DX))/(H*H)
!       DH = (X*DX + Y*DY)/H
!       DS = (60.0*FACT*(H*DZ - Z*DH))/(F*F)
!       DF = (H*DH + Z*DZ)/F
! C
!       IF (IDM.EQ.1) THEN
!        WRITE(IU,930) DATE,LTD,LTM,TYPE,LND,LNM,ALT,NAME
!   930  FORMAT (1X,F8.3,' Lat',2I4,A11,' Long ',2I4,F10.3,' km ',A20)
!       ELSE
!        WRITE(IU,931) DATE,XLT,TYPE,XLN,ALT,NAME
!   931  FORMAT (1X,F8.3,' Lat',F8.3,A11,' Long ',F8.3,F10.3,' km ',A20)
!       ENDIF
! C
!       IDD = NINT(DD)
!       WRITE(IU,937) IDEC,IDECM,IDD
!   937 FORMAT (15X,'D =',I5,' deg',I4,' min',4X,'SV =',I8,' min/yr')
! C
!       IDS = NINT(DS)
!       WRITE(IU,939) INC,INCM,IDS
!   939 FORMAT (15X,'I =',I5,' deg',I4,' min',4X,'SV =',I8,' min/yr')
! C
!       IH = NINT(H)
!       IDH = NINT(DH)
!       WRITE(IU,941) IH,IDH
!   941 FORMAT (15X,'H =',I8,' nT     ',5X,'SV =',I8,' nT/yr')
! C
!       IX = NINT(X)
!       IDX = NINT(DX)
!       WRITE(IU,943) IX,IDX
!   943 FORMAT (15X,'X =',I8,' nT     ',5X,'SV =',I8,' nT/yr')
! C
!       IY = NINT(Y)
!       IDY = NINT(DY)
!       WRITE(IU,945) IY,IDY
!   945 FORMAT (15X,'Y =',I8,' nT     ',5X,'SV =',I8,' nT/yr')
! C
!       IZ = NINT(Z)
!       IDZ = NINT(DZ)
!       WRITE(IU,947) IZ,IDZ
!   947 FORMAT (15X,'Z =',I8,' nT     ',5X,'SV =',I8,' nT/yr')
! C
!       NF = NINT(F)
!       IDF = NINT(DF)
!       WRITE(IU,949) NF,IDF
!   949 FORMAT (15X,'F =',I8,' nT     ',5X,'SV =',I8,' nT/yr'/)
! C
!       GO TO 40
! C
!    60 CONTINUE
! C
! C     SERIES OF VALUES AT ONE LOCATION...
! C
!       IF (IDM.EQ.1) THEN
!        WRITE(IU,932) LTD,LTM,TYPE,LND,LNM,ALT,NAME
!   932  FORMAT ('Lat',2I4,A11,'  Long ',2I4,F10.3,' km ',A20)
!       ELSE
!        WRITE(IU,933) XLT,TYPE,XLN,ALT,NAME
!   933  FORMAT ('Lat',F8.3,A11,'  Long ',F8.3,F10.3,' km ',A20)
!       ENDIF
!       WRITE (IU,934)
!   934 FORMAT (3X,'DATE',7X,'D',3X,'SV',6X,'I',2X,'SV',6X,'H',4X,'SV',
!      17X,'X',4X,'SV',7X,'Y',4X,'SV',7X,'Z',4X,'SV',6X,'F',4X,'SV')
!       IMX = DTMX - DTMN - 5
!       DO 70 I = 1,IMX
!       DATE = DTMN - 0.5 + I
!       CALL IGRF12SYN (0,DATE,ITYPE,ALT,CLT,XLN,X,Y,Z,F)
!       D = FACT*ATAN2(Y,X)
!       H = SQRT(X*X + Y*Y)
!       S = FACT*ATAN2(Z,H)
!       IH = NINT(H)
!       IX = NINT(X)
!       IY = NINT(Y)
!       IZ = NINT(Z)
!       NF = NINT(F)
! C
!       CALL IGRF12SYN (1,DATE,ITYPE,ALT,CLT,XLN,DX,DY,DZ,F1)
!       DD = (60.0*FACT*(X*DY - Y*DX))/(H*H)
!       DH = (X*DX + Y*DY)/H
!       DS = (60.0*FACT*(H*DZ - Z*DH))/(F*F)
!       DF = (H*DH + Z*DZ)/F
!       IDD = NINT(DD)
!       IDH = NINT(DH)
!       IDS = NINT(DS)
!       IDX = NINT(DX)
!       IDY = NINT(DY)
!       IDZ = NINT(DZ)
!       IDF = NINT(DF)
! C
!       WRITE(IU,935)
!      1   DATE,D,IDD,S,IDS,IH,IDH,IX,IDX,IY,IDY,IZ,IDZ,NF,IDF
!   935 FORMAT(1X,F6.1,F8.2,I5,F7.2,I4,I7,I6,3(I8,I6),I7,I6)
!    70 CONTINUE
!       IFL = 2
!       GOTO 158
C
C     GRID OF VALUES...
C
  150 NPTS=0 ! LMK Following SdL
!   150 WRITE(6,*)'Enter value for MF/SV flag:'
!       WRITE(6,*)'0 for main field (MF)'
!       WRITE(6,*)'1 for secular variation (SV)'
!       WRITE(6,*)'2 for both'
!       WRITE(6,*)'9 to quit'
!       READ (5,*) IFL
!       IF (IFL.EQ.9) STOP
!       IF (IFL.NE.0.AND.IFL.NE.1.AND.IFL.NE.2) GOTO 150
! C
!       WRITE(6,*) 'Enter initial value, final value & increment or'
!       WRITE(6,*) 'decrement of latitude, in degrees & decimals'
!       READ (5,*) XLTI,XLTF,XLTD
      LTI = NINT(1000.0*XLTI)
      LTF = NINT(1000.0*XLTF)
      LTD = NINT(1000.0*XLTD)
!      WRITE(6,*) 'Enter initial value, final value & increment or'
!      WRITE(6,*) 'decrement of longitude, in degrees & decimals'
!      READ (5,*) XLNI,XLNF,XLND
      LNI = NINT(1000.0*XLNI)
      LNF = NINT(1000.0*XLNF)
      LND = NINT(1000.0*XLND)
      IF (LTI.LT.-90000.OR.LTI.GT.90000) GO TO 206
      IF (LTF.LT.-90000.OR.LTF.GT.90000) GO TO 206
      IF (LNI.LT.-360000.OR.LNI.GT.360000) GO TO 207
      IF (LNF.LT.-360000.OR.LNF.GT.360000) GO TO 207
!   98 WRITE(6,*) 'Enter date in years A.D.'
!      READ (5,*) DATE
      IF (DATE.LT.DTMN.OR.DATE.GT.DTMX) GO TO 209
!      IF (ITYPE.EQ.1) THEN
!       WRITE(6,*) 'Enter altitude in km'
!      ELSE
!       WRITE(6,*) 'Enter radial distance in km (>3485 km)'
!      END IF
!      READ (5,*) ALT
      IF (ITYPE.EQ.2.AND.ALT.LE.3485.0) GO TO 210
! SdL leaves this in, I don't think I want it
      WRITE(IU,958) DATE,ALT,TYPE
  958 FORMAT (' Date =',F9.3,5X,'Altitude =',F10.3,' km',5X,A11//
     1        '      Lat     Long',7X,'D',7X,'I',7X,'H',7X,'X',7X,'Y',
     2        7X,'Z',7X,'F')
C
      LT = LTI
  151 XLT = LT
      XLT = 0.001*XLT
      CLT = 90.0 - XLT
      IF (CLT.LT.-0.001.OR.CLT.GT.180.001) GO TO 202
      LN = LNI
  152 XLN = LN
      XLN = 0.001*XLN
      IF (XLN.LE.-360.0) XLN = XLN + 360.0
      IF (XLN.GE.360.0) XLN = XLN - 360.0
      CALL IGRF12SYN (0,DATE,ITYPE,ALT,CLT,XLN,X,Y,Z,F)
      D = FACT*ATAN2(Y,X)
      H = SQRT(X*X + Y*Y)
      S = FACT*ATAN2(Z,H)
      IH = NINT(H)
      IX = NINT(X)
      IY = NINT(Y)
      IZ = NINT(Z)
      NF = NINT(F)
      IF (IFL.EQ.0) GOTO 153
      CALL IGRF12SYN (1,DATE,ITYPE,ALT,CLT,XLN,DX,DY,DZ,F1)
      IDX = NINT(DX)
      IDY = NINT(DY)
      IDZ = NINT(DZ)
      DD = (60.0*FACT*(X*DY - Y*DX))/(H*H)
      IDD = NINT(DD)
      DH = (X*DX + Y*DY)/H
      IDH = NINT(DH)
      DS = (60.0*FACT*(H*DZ - Z*DH))/(F*F)
      IDS = NINT(DS)
      DF = (H*DH + Z*DZ)/F
      IDF = NINT(DF)
C
  153 CONTINUE
      IF (IFL.EQ.0) WRITE(IU,959) XLT,XLN,D,S,IH,IX,IY,IZ,NF
      IF (IFL.EQ.1) WRITE(IU,960) XLT,XLN,IDD,IDS,IDH,IDX,IDY,IDZ,IDF
      IF (IFL.EQ.2) THEN
       WRITE(IU,959) XLT,XLN,D,S,IH,IX,IY,IZ,NF
       WRITE(IU,961) IDD,IDS,IDH,IDX,IDY,IDZ,IDF
      ENDIF      
  959 FORMAT (2F9.3,2F8.2,5I8)
  960 FORMAT (2F9.3,7I8)
  961 FORMAT (14X,'SV: ',7I8)
C
  154 LN = LN + LND
      IF (LND.LT.0) GO TO 156
      IF (LN.LE.LNF) GO TO 152
  155 LT = LT + LTD
      IF (LTD.LT.0) GO TO 157
      IF (LT - LTF) 151,151,158
  156 IF (LN - LNF) 155,152,152
  157 IF (LT.GE.LTF) GO TO 151
  158 CONTINUE
      IF (IFL.EQ.0.OR.IFL.EQ.2) THEN
       WRITE(IU,962)
  962  FORMAT (/' D is declination in degrees (+ve east)'/
     1          ' I is inclination in degrees (+ve down)'/
     2          ' H is horizontal intensity in nT'/
     3          ' X is north component in nT'/
     4          ' Y is east component in nT'/
     5          ' Z is vertical component in nT (+ve down)'/
     6          ' F is total intensity in nT')
      IF (IFL.NE.0) WRITE(IU,963)
  963  FORMAT (' SV is secular variation (annual rate of change)'/
     1' Units for SV: minutes/yr (D & I); nT/yr (H,X,Y,Z & F)')
      IF (ITYPE.EQ.2) WRITE(IU,*)
     1'These elements are relative to the geocentric coordinate system'
      ELSE
       WRITE(IU,964)
  964  FORMAT (/' D is SV in declination in minutes/yr (+ve east)'/
     1          ' I is SV in inclination in minutes/yr (+ve down)'/
     2          ' H is SV in horizontal intensity in nT/yr'/
     3          ' X is SV in north component in nT/yr'/
     4          ' Y is SV in east component in nT/yr'/
     5          ' Z is SV in vertical component in nT/yr (+ve down)'/
     6          ' F is SV in total intensity in nT/yr')
      IF (ITYPE.EQ.2) WRITE(IU,*)
     1'These elements are relative to the geocentric coordinate system'
      ENDIF
!  159 STOP
  159 RETURN    ! Edit LMK
C
  209 WRITE(6,972) DATE
  972 FORMAT (' ***** Error *****'/' DATE =',F9.3,
     1        ' - out of range')
!      STOP
      RETURN ! LMK
C
  210 WRITE(6,973) ALT,ITYPE
  973 FORMAT (' ***** Error *****'/' A value of ALT =',F10.3,
     1        ' is not allowed when ITYPE =',I2)
!      STOP
      RETURN ! LMK
C
  202 WRITE(6,966) XLT
  966 FORMAT (' ***** Error *****'/' XLT =',F9.3,
     1        ' - out of range')
!      STOP
      RETURN ! LMK

C
  203 WRITE(6,967) XLN
  967 FORMAT (' ***** Error *****'/' XLN =',F10.3,
     1        ' - out of range')
!      STOP
      RETURN ! LMK

C
  204 WRITE(6,968) LTD,LTM
  968 FORMAT (' ***** Error *****'/' Latitude out of range',
     1        ' - LTD =',I6,5X,'LTM =',I4)
!      STOP
      RETURN ! LMK

C
  205 WRITE(6,969) LND,LNM
  969 FORMAT (' ***** Error *****'/' Longitude out of range',
     1        ' - LND =',I8,5X,'LNM =',I4)
!      STOP
      RETURN ! LMK

C
  206 WRITE(6,970) LTI,LTF
  970 FORMAT (' ***** Error *****'/
     1        ' Latitude limits of table out of range - LTI =',
     2        I6,5X,' LTF =',I6)
!      STOP
      RETURN ! LMK

C
  207 WRITE(6,971) LNI,LNF
  971 FORMAT (' ***** Error *****'/
     1        ' Longitude limits of table out of range - LNI =',
     2        I8,5X,' LNF =',I8)
!      STOP
      RETURN ! LMK

C
  208 WRITE(6,974) ITYPE
  974 FORMAT (' ***** Error *****'/
     1        ' ITYPE:',I8,' is not 1 or 2')
!      STOP
      RETURN ! LMK

      END
C END SUBROUTINE IGRF12
C
      SUBROUTINE DMDDEC (I,M,X)
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
Cf2py intent(in) I
Cf2py intent(in) M
Cf2py intent(out) X
      DE = I
      EM = M
      IF (I.LT.0) EM = -EM
      X = DE + EM/60.0
      RETURN
      END
C
      SUBROUTINE DDECDM (X,I,M)
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
Cf2py intent(in) X
Cf2py intent(out) I
Cf2py intent(out) M
      SIG = SIGN(1.1D0,X)
      DR = ABS(X)
      I = INT(DR)
      T = I
      M = NINT(60.*(DR - T))
      IF (M.EQ.60) THEN
       M = 0
       I = I + 1
      ENDIF
      ISIG = INT(SIG)
      IF (I.NE.0) THEN
       I = I * ISIG
      ELSE
       IF (M.NE.0) M = M * ISIG
      ENDIF
      RETURN
      ENDs