# Procedury

W taryfikatorze w SASie przy przeliczaniu cen procedur z CP brano pod uwagę (z zachowaniem priorytetu tj. cena przypisana z kategorii wyżej jezeli kategoria niżej ma brak) po odcięciu BOXPLOT, średnia arytmetyczna (nieważona) z procedur CP:

1. Koszty procedury u świadczeniodawcy (grupowanie na: kod_sw icd_9 nazwa_pr nr_opk_pr).
1. Koszt procedury w całej bazie (grupowanie na: icd_9 nazwa_pr)

W pytarze do przypisywania cen wzięto pod uwagę (w wyniku rozmów z analitykami, z zachowaniem priorytetu):

1. W badanej populacji:

    1. Grupowanie po 'icd_9', 'nazwa_pr','nr_opk_pr', 'kod_sw'.
    1. Grupowanie po 'icd_9', 'nazwa_pr', 'kod_sw'.
    1. Grupowanie po 'icd_9', 'nazwa_pr'.
    
1. W całej bazie:
 
    1. Grupowanie po 'icd_9', 'nazwa_pr'.

#### Obliczanie kosztu pr_hr
Koszt pr_hr jest obliczany z 4 tabel:

1. PR_HR_PERS_CZAS - czas jaki personel spędza przy zabiegu (jeżeli jest kilka osób tego samego personelu to czas sumuję się dla każdej, czyli 2 osoby po 1h to jest jeden wpis 2h)
1. PR_HR_PERS_WAGI - wagi (z których opków) będzie policzone wynagrodzenie dla tego personelu
1. PR_HR_INFRAST_WAGI - wagi OPK dla infrastruktury w tym oddziale
1. PR_HR_INFRAST_CZAS - czas zabiegu