import pygame, math, numpy as np, matplotlib.pyplot as plt

# Brukerinput (Fart på hoppkanten, vikel på hoppkanten, og hvilke grafer som skal vises)
v_0 = float(input("Speed (m/s): "))
θ_0 = math.radians(float(input("Angle (°): ")))
graph = str(input('Graphset ("pos","vec","both","ang","all","none"): ')) # Grafer er for dypere informasjon og debugging

# Dekomponerer fartsvektoren
v_x_0 = math.cos(θ_0) * v_0
v_y_0 = math.sin(θ_0) * v_0


# Lager funskjon som gjør det lettere å definere, adskille og bruke vektorer
def vec(x, y):
    return np.array([x, y])

# Konstanter
k = 0.4  # Luftmotstandskoeffisient, 0.4 er litt høyere enn ERGO 1 sin fallskjermhopper
# Luftmotstandskoeffisient eksempler fra ERGO 1 boka: Fallskjermhopper: 0.29, gjenstand: 0.7 muffinsformer: 9.6
m = 70  # Masse på ca. 70kg med kroppsvekten min + utstyr
g = vec(0, 9.81)  # Gravitasjonsakselerasjon på 9.81(Jorda)
PPS = 50  # Points per second, høyere tall er mer nøyaktig, men simuleringen blir tungere for maskinen
SNOWBOARDER_W = 1.50  # Mitt snowboards lengde i meter
SNOWBOARDER_H = 1.80  # Min høyde i meter


# Modellering

# Strekning med konstant akselerasjon
def strekning_ka(t, a, v):
    return (1/2)*a*t**2 + v*t


# Denne funskjonen brukes til å finne effekten luftmotstand har på bevegelseskurven (altså bevegelseskurven uten luftmotstand)
def uten_luftmotstand():
    t = 0  # Tid

    # Verdier for y:
    a = -g[1]
    v = v_y_0

    # Regner ut sekundet der snowboarderen treffer bakken
    while strekning_ka(t, a, v) >= 0:
        t += 1

    # Setter opp tiden og posisjonene til y aksen med {PPS} punkter i sekundet
    time = np.linspace(0, t, t*PPS)
    posy = strekning_ka(time, a, v)

    # Regner ut punktet snowboarderen treffer bakken med {PPS} punkt i sekundet nøyaktighet
    for i in range(t*PPS):
        if posy[i] < 0:
            groundpoint = i+1
            break

    # Justerer arrayene slik de passer med landingspunktet
    time = time[0:groundpoint]
    posy = posy[0:groundpoint]

    # Lager punkter for x aksen
    a = 0
    v = v_x_0
    posx = strekning_ka(time, a, v)

    return [posx, posy, time]


# Regner ut summen av krefter basert på en fart og konstantene
def a(v):
    L = vec(-k*v[0]*abs(v[0]),
            -k*v[1]*abs(v[1]))
    G = m * -g
    F = G+L

    return F/m


# Denne funskjonen brukes til å lage dataene til simuleringen
def med_luftmotstand():
    t = 0
    x = 0
    y = 0
    v = vec(v_x_0, v_y_0)

    # Definerer datalister til simuleringen med første verdier
    posx = [0]
    posy = [0]
    time = [0]
    v_x = [v[0]]
    v_y = [v[1]]
    a_x = [a(v)[0]]
    a_y = [a(v)[1]]
    θ = [math.degrees(θ_0)]

    max_y = 0  # Skal brukes til skalere simuleringen


    # Regner ut alle verdiene og legger dem til listene fram til bakken treffes
    while y >= 0:

        t += 1/PPS
        time.append(t)

        v += a(v)/PPS

        x += v[0]/PPS
        posx.append(x)

        y += v[1]/PPS
        posy.append(y)

        v_x.append(v[0])
        v_y.append(v[1])

        a_x.append(a(v)[0])
        a_y.append(a(v)[1])

        θ.append(math.degrees(math.atan(v[1]/v[0])))

        if y > max_y:
            max_y = y

    return [posx, posy, time, v_x, v_y, max_y, θ, a_x, a_y]


# Grafering

# Funksjon som gjør opprettelsen av subplot enkel og fin
def subplot(plot, title, arrx, arry, label, c):
    plot.set_title(title)
    plot.plot(arrx, arry, label = label, c = c)
    plot.grid(True)
    plot.legend()


# Henter ut verdiene fra funksjonene
u_luftmotstand = uten_luftmotstand()
xpos, ypos, time, v_x, v_y, max_y, θ_uglattet, a_x, a_y = med_luftmotstand()


# k er tallet som brukes til å bestemme hvor grov glattingen skal være
k = int(round(time[-1]*PPS/4, 0))

θ = []

# Sørger for at hele definisjonsmengden har en verdi
# (Det blir små hopp i grafen, men de er såpass små at de ikke har synlig uttelling)
for i in range(k):
    θ.append(θ_uglattet[i])

for i in range(k, len(θ_uglattet)-k):
    θ.append(np.mean(θ_uglattet[(i-k) : (i+k)]))  # Regner ut gjennomsnitt av intervallet k slik rotasjonen i luften blir glattere

for i in range(k):
    θ.append(θ_uglattet[i-k-1])

# Merk at det er ikke alltid at den glattede kurven er bedre, men i veldig slake, eller skarpe bevegelser utgjør det en god forskjell.
# Dette er lik rotasjonen i det hele tatt, bare en visuell endring, som får hoppet til å se enda mer naturlig ut


# Grafer for debugging og dypere informasjon
if graph in ("ang","all"):
    # Plotter den glattede og uglattede vinkel mot hverandre, for å se om den glattede er bedre
    plt.plot(time, θ_uglattet, label = "Uglattet", c="blue")
    plt.plot(time, θ, label = "Glattet", c="red")
    plt.title("Vinkel på snowboarder")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (\u00b0)")
    plt.grid()
    plt.legend()


if graph in ("pos","both","all"):
    # Plotter posisjonsdata for med og uten luftmotstand, både som en strekningskurve og som x og y posisjon plottet seperat mot tiden
    # Dette lar meg se nærmere på bevegelsen og sammenligne med og uten luftmotstand
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.suptitle('Position data')

    subplot(ax1, "ax1", u_luftmotstand[0], u_luftmotstand[1], "Uten luftmotstand", "green")
    subplot(ax1, "Position (X pos, Y pos)", xpos, ypos, "Med luftmotstand", "red")

    subplot(ax2, "ax2", u_luftmotstand[2], u_luftmotstand[1], "Uten luftmotstand", "green")
    subplot(ax2, "Vertical disposition (Y pos)", time, ypos, "Med luftmotstand", "red")

    subplot(ax3, "ax3", u_luftmotstand[2], u_luftmotstand[0], "Uten luftmotstand", "green")
    subplot(ax3, "Horizontal disposition (X pos)", time, xpos, "Med luftmotstand", "red")

if graph in ("vec","both","all"):
    # Plotter den dekomponerte farten og akkselerasjonen i hvert sitt subplot
    # Dette lar meg se nærmere på utslaget til luftmotstanden og feilsøke programmet
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
    fig.suptitle('Vector data')

    subplot(ax1, "Velocity X (m/s)", time, v_x, "Velocity", "blue")
    subplot(ax2, "Acceleration X (m/s**2)", time, a_x, "Acceleration", "red")

    subplot(ax3, "Velocity Y (m/s)", time, v_y, "Velocity", "blue")
    subplot(ax4, "Acceleration Y (m/s**2)", time, a_y, "Acceleration", "red")

tp = 0

for i in range(len(ypos)):
    if ypos[tp] < ypos[i]:
        tp = i

plt.show()




# Simulering

pygame.init()

clock = pygame.time.Clock()
width = 1800
height = 900

# Finner den laveste mulige meterlengden i pixler vertikalt og horisontalt, og bruker den laveste, slik simuleringen ikke forlater skjermen.
min_meter_x = width/(xpos[-1]+SNOWBOARDER_W*2)
min_meter_y = height/(max_y+SNOWBOARDER_H*2)
if min_meter_x > min_meter_y:
    meter = min_meter_y
else:
    meter = min_meter_x


font = pygame.font.Font("freesansbold.ttf", int(round(width/50, 0)))
screen = pygame.display.set_mode((width, height))
running = True
t = 0


while running:

    # Bruker try except, slik simuleringen automatisk stopper når t er out of range
    try:
        screen.fill((255, 255, 255))

        # Regner ut x og y posisjon på en måte slik snowboarderen ikke blir feilplassert i forhold til meterlengden og høyden sin.
        x = xpos[t]*meter
        y = height - (ypos[t] + SNOWBOARDER_H)*meter

        # Laster inn snowboarder bildet, skalerer det, roterer det og plasserer det på skjermen
        # Dette må gjøres på nytt hver tick, fordi bildet endres/ødelegges litt hver gang det roterer.
        snowboarder = pygame.image.load("ProgModX/snowboarder.png").convert()
        snowboarder = pygame.transform.scale(snowboarder, (SNOWBOARDER_W*meter, SNOWBOARDER_H*meter))
        snowboarder = pygame.transform.rotate(snowboarder, θ[t])
        screen.blit(snowboarder, (x, y))

        # Skriver data fra hoppet til skjermen
        skrift = font.render(f"Time: {t/PPS:<.2f}s  Height: {ypos[t]:<.1f}m  Length: {xpos[t]:<.1f}m", True, (0,0,0))
        screen.blit(skrift, (0,0))

    except:

        # Skriver dataene fra hoppet til konsollen
        print (f"Time: {(t-1)/PPS:.2f}s  Max height: {max_y:.1f}m  Length: {xpos[t-1]:.1f}m  Landing angle: {θ_uglattet[t-1]:.0f}\u00b0")
        pygame.time.wait(1000)
        running = False

    clock.tick(PPS)
    t += 1
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
