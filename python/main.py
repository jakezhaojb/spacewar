"""main module, starts game and main loop"""

import pygame
import var, gfx, snd, txt, input
import allmodules
import gamepref
import ai

#at this point, all needed pygame modules should
#be imported, so they can be initialized at the
#start of main()

def main(args):
    try:
        gamemain(args)
    except KeyboardInterrupt:
        print 'Keyboard Interrupt...'
        print 'Exiting'


def gamemain(args):
    #initialize all our code (not load resources)
    pygame.init()
    var.clock = pygame.time.Clock()

    input.load_translations()
    gamepref.load_prefs()

    if '-aitrain' in args:
        var.ai_train = 1

    # number of players
    if '-one' in args:
        var.numplayers = 1
    elif '-two' in args:
        var.numplayers = 2
    elif '-three' in args:
        var.numplayers = 3
    else:
        var.numplayers = 4

    size = 800, 600
    full = var.display
    if '-window' in args:
        full = 0
    gfx.initialize(size, full)
    #pygame.display.set_caption('Spacewar')

    if not '-nosound' in args:
        if not var.ai_train:
            snd.initialize()
    input.init()

    if not txt.initialize():
        raise pygame.error, "Pygame Font Module Unable to Initialize"

    #create the starting game handler
    from gameinit import GameInit
    from gamemenu import GameMenu
    from gamefinish import GameFinish
    var.handler = GameInit(GameFinish(None))

    #set timer to control stars..
    pygame.time.set_timer(pygame.USEREVENT, 1000)


    #psyco.full()
    gamestart = pygame.time.get_ticks()
    numframes = 0
    #random.seed(0)
    menuenter = 0

    #main game loop
    lasthandler = None
    while var.handler:
        numframes += 1
        handler = var.handler
        if handler != lasthandler:
            lasthandler = handler
            if hasattr(handler, 'starting'):
                handler.starting()
        if (not isinstance(handler, GameMenu)) or menuenter == 1:
        #if True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    fps = var.clock.get_fps()
                    print 'FRAMERATE: %f fps' % fps
                    gfx.starobj.recalc_num_stars(fps)
                    continue
                elif event.type == pygame.ACTIVEEVENT:
                    if event.state == 4 and event.gain:
                        #uniconified, lets try to kick the screen
                        pygame.display.update()
                    elif event.state == 2:
                        if hasattr(var.handler, 'gotfocus'):
                            if event.gain:
                                var.handler.gotfocus()
                            else:
                                var.handler.lostfocus()
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if event.mod&pygame.KMOD_ALT:
                        var.display = not var.display
                        gfx.switchfullscreen()
                        continue
                inputevent = input.translate(event)
                #print(event.dict, event.type)
                #print(event, inputevent)
                if inputevent.normalized != None:
                    inputevent = input.exclusive((input.UP, input.DOWN, input.LEFT, input.RIGHT), inputevent)
                    handler.input(inputevent)
                elif event.type == pygame.QUIT:
                    var.handler = None
                    break
                handler.event(event)
        else:
            newdict = {}
            newdict['normalized'] = 13
            newdict['translated'] = 5
            newdict['all'] = 0
            newdict['release'] = 0
            newdict['normalized'] = 310
            newdict['key'] = 310
            newdict['mod'] = 0
            inputevent = pygame.event.Event(3, newdict)
            if inputevent.normalized != None:
                inputevent = input.exclusive((input.UP, input.DOWN, input.LEFT, input.RIGHT), inputevent)
                handler.input(inputevent)
            handler.event(inputevent)
            menuenter = 1  # flag: done

        handler.run()
        # If in AI training mode then don't slow frame rate
        if var.ai_train and hasattr(handler,'start_player'):
            pass
        else:
            var.clockticks = var.clock.tick(var.frames_per_sec)
        gfx.update()
        while not pygame.display.get_active():
            pygame.time.wait(100)
            pygame.event.pump()

        #pygame.time.wait(10)

    gameend = pygame.time.get_ticks()
    runtime = (gameend - gamestart) / 1000.0
    #print "FINAL FRAMERATE: ", numframes, runtime, numframes/runtime


    #game is finished at this point, do any
    #uninitialization needed
    input.save_translations()
    gamepref.save_prefs()
    pygame.quit()


