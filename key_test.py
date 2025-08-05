import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("键盘测试器")

font = pygame.font.SysFont(None, 36)

def main():
    while True:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                print(f"按键代码: {event.key}, Unicode: {repr(event.unicode)}")
                
                # 显示在屏幕上
                text = font.render(f"按下: {event.key} ({event.unicode})", True, (255, 255, 255))
                screen.blit(text, (50, 100))
                
                if event.key == pygame.K_e or event.unicode == 'e':
                    print("=== E键被正确识别 ===")
                    text = font.render("E键已识别!", True, (0, 255, 0))
                    screen.blit(text, (50, 150))
        
        pygame.display.flip()

if __name__ == "__main__":
    main()