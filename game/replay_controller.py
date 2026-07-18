"""Replay controller placeholder."""
from core.enums import Move

class ReplayController:
    """
    Quản lý việc phát lại (animate) chuỗi bước đi (actions) 
    sau khi thuật toán AI đã tìm ra đường đến đích.
    """
    
    def __init__(self):
        self.actions: list[Move] = []
        self.current_step = 0
        self.is_replaying = False

    def trigger_replay(self, actions: list[Move]):
        """
        Nhận mảng các nước đi từ AI Result và kích hoạt trạng thái phát lại.
        
        Args:
            actions: Danh sách các Move ví dụ [Move.UP, Move.RIGHT, Move.DOWN]
        """
        self.actions = actions
        self.current_step = 0
        self.is_replaying = True
        print(f"[ReplayController] Bắt đầu replay với {len(actions)} bước.")

    def get_next_move(self) -> Move | None:
        """
        Lấy nước đi tiếp theo để game loop thực thi và render.
        Trả về None nếu đã phát lại xong.
        """
        if not self.is_replaying or self.current_step >= len(self.actions):
            self.is_replaying = False
            return None
        
        move = self.actions[self.current_step]
        self.current_step += 1
        return move
