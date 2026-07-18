# BÁO CÁO CÀI ĐẶT SWITCH, BRIDGE VÀ THUẬT TOÁN A*

## PHẦN A — GIẢI THÍCH THAY ĐỔI THEO TỪNG FILE

Phần này được sắp xếp theo đường dẫn file. Mỗi mục chỉ tập trung vào code đã thêm hoặc sửa so với phiên bản ban đầu. Phần giải thích thuật toán và logic tổng quát được giữ ở Phần B bên dưới.

### 1. `.vscode/settings.json`

Diff hiện tại đổi môi trường Python mặc định của VS Code:

```json
"python-envs.defaultEnvManager": "ms-python.python:venv",
"python-envs.defaultPackageManager": "ms-python.python:pip"
```

Hai giá trị cũ là `conda`. Thay đổi này chỉ ảnh hưởng cách VS Code đề xuất tạo môi trường và cài package; nó không thay đổi luật game hoặc A*. Đây là thay đổi cấu hình workspace đã tồn tại trong working tree, không phải phần cốt lõi của chức năng switch/bridge.

### 2. `REPORT.md`

Đây là file báo cáo mới. File ghi lại:

- Các thay đổi theo từng source file.
- Cấu trúc dữ liệu switch và bridge.
- Giải thích chi tiết A*.
- Cách A* liên kết với transition model và giao diện.
- Các test đã thêm và giới hạn hiện tại.

File này không được import hoặc chạy bởi chương trình.

### 3. `ai/astar.py`

File ban đầu chỉ có placeholder. Toàn bộ phần cài đặt A* là code mới.

#### Import priority queue

```python
from heapq import heappop, heappush
from itertools import count
```

- `heappush` đưa node vào min-heap.
- `heappop` lấy node có priority nhỏ nhất.
- `count` sinh số thứ tự để phá hòa giữa các node.

#### Import các thành phần của bài toán

```python
from ai.heuristics import goal_distance
from ai.result import SearchResult
from core.board import Board
from core.enums import Move
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state
```

A* không tự cài luật di chuyển. Nó nhận successor từ `get_valid_moves` và kiểm tra đích bằng `is_goal_state`.

#### Hàm `_reconstruct_moves`

```python
def _reconstruct_moves(
    parents: dict[GameState, tuple[GameState, Move]],
    state: GameState,
) -> tuple[Move, ...]:
```

`parents` ánh xạ một state con sang `(state cha, move)`. Hàm bắt đầu từ goal và đi ngược về initial state:

```python
moves: list[Move] = []

while state in parents:
    state, move = parents[state]
    moves.append(move)
```

Các move thu được đang theo thứ tự goal về start, nên:

```python
moves.reverse()
return tuple(moves)
```

#### Hàm `solve_astar`

```python
sequence = count()
frontier: list[tuple[int, int, int, GameState]] = []
```

Mỗi entry trong heap có dạng:

```text
(f, g, sequence, state)
```

`sequence` ngăn Python phải so sánh trực tiếp hai `GameState` nếu `f` và `g` bằng nhau.

```python
best_cost: dict[GameState, int] = {initial_state: 0}
parents: dict[GameState, tuple[GameState, Move]] = {}
expanded_nodes = 0
```

- `best_cost`: `g` nhỏ nhất đã biết cho mỗi state.
- `parents`: dữ liệu để dựng lại lời giải.
- `expanded_nodes`: số node đã mở rộng.

Initial state được đưa vào heap bằng:

```python
heappush(
    frontier,
    (goal_distance(board, initial_state), 0, next(sequence), initial_state),
)
```

Vì `g(start)=0`, priority ban đầu bằng `h(start)`.

Vòng lặp chính:

```python
while frontier:
    _, cost, _, state = heappop(frontier)
```

Luôn lấy state có `f` nhỏ nhất.

```python
if cost != best_cost.get(state):
    continue
```

Loại entry cũ nếu sau đó đã tìm được đường rẻ hơn đến cùng state.

```python
if is_goal_state(board, state):
    moves = _reconstruct_moves(parents, state)
    return SearchResult(moves, cost, expanded_nodes)
```

Chỉ trả kết quả khi goal được pop khỏi heap. Đây là thời điểm đường đi được xác nhận tối ưu với heuristic hiện tại.

```python
for move, next_state in get_valid_moves(board, state):
    next_cost = cost + get_step_cost(board, state, next_state)
```

Sinh tối đa bốn successor và cộng chi phí tile của state đích. Block nằm trên hai ô dùng chi phí lớn nhất, không cộng hai ô.

```python
if next_cost >= best_cost.get(next_state, float("inf")):
    continue
```

Bỏ đường mới nếu không tốt hơn đường đã biết.

```python
best_cost[next_state] = next_cost
parents[next_state] = (state, move)
priority = next_cost + goal_distance(board, next_state)
```

Cập nhật `g`, cha và `f=g+h`.

```python
heappush(
    frontier,
    (priority, next_cost, next(sequence), next_state),
)
```

Đưa successor vào heap để xét sau.

```python
return SearchResult.no_solution(expanded_nodes)
```

Chỉ chạy khi heap rỗng mà không tìm được goal.

### 4. `ai/heuristics.py`

File placeholder được thay bằng hàm heuristic:

```python
from math import ceil
```

`ceil` làm tròn lên kết quả chia cho 2.

```python
def goal_distance(board: Board, state: GameState) -> int:
```

Nhận board và state để tính `h(n)`.

```python
goal_row, goal_col = board.find_goal()
```

Lấy tọa độ goal.

```python
distance = min(
    abs(row - goal_row) + abs(col - goal_col)
    for row, col in state.block.occupied_cells()
)
```

Tính Manhattan distance từ từng ô block chiếm đến goal và chọn giá trị nhỏ nhất. Block đứng có một ô; block nằm có hai ô.

```python
return ceil(distance / 2)
```

Một lần lăn có thể tiến tối đa hai ô nên chia khoảng cách cho 2. `ceil` bảo đảm khoảng cách lẻ được làm tròn lên.

### 4.1. `ai/problem.py`

File placeholder được thay bằng mô hình chi phí dùng chung cho A* và UCS.

```python
NORMAL_STEP_COST = 1
SWITCH_ACTIVATION_COST = 2
FRAGILE_STEP_COST = 5
```

Ba hằng số tách chính sách chi phí khỏi code solver. Cost 2 chỉ áp dụng khi switch thực sự làm thay đổi `bridge_states`.

```python
MINIMUM_STEP_COST = NORMAL_STEP_COST
```

Giá trị nhỏ nhất được heuristic dùng làm lower bound.

```python
if current_state.bridge_states != next_state.bridge_states:
    return SWITCH_ACTIVATION_COST

if any(
    board.get_tile(row, col) == TileType.FRAGILE
    for row, col in next_state.block.occupied_cells()
):
    return FRAGILE_STEP_COST

return NORMAL_STEP_COST
```

`get_step_cost` tính cost của transition từ current state sang next state. Bridge state thay đổi có cost 2; chạm fragile có cost 5; các bước còn lại có cost 1. Vì cost không cộng theo số ô, block nằm không bị phạt gấp đôi.

`KeyError` được đổi thành `ValueError` có thông báo rõ nếu một loại tile walkable chưa được khai báo cost.

### 5. `ai/result.py`

File placeholder được thay bằng dataclass:

```python
@dataclass(frozen=True)
class SearchResult:
```

`frozen=True` làm object bất biến.

```python
moves: tuple[Move, ...]
cost: int
expanded_nodes: int
solved: bool = True
```

- `moves`: lời giải.
- `cost`: tổng chi phí terrain của đường đi; không nhất thiết bằng số bước.
- `expanded_nodes`: số state đã mở rộng.
- `solved`: tìm thấy lời giải hay không.

```python
@classmethod
def no_solution(cls, expanded_nodes: int) -> "SearchResult":
    return cls((), 0, expanded_nodes, False)
```

Tạo kết quả thất bại thống nhất cho solver.

### 5.1. `ai/ucs.py`

File placeholder được thay bằng Uniform-Cost Search hoàn chỉnh.

UCS dùng cùng `get_step_cost` với A*, nhưng entry heap chỉ cần:

```text
(g, sequence, state)
```

Priority của UCS là tổng chi phí thật `g`, không cộng heuristic. `best_cost`, stale-entry check và `parents` hoạt động giống A*. Vì hai solver dùng chung transition và cost function, kết quả tối ưu của chúng phải có cùng tổng cost; test suite dùng tính chất này để kiểm tra A*.

### 6. `core/board.py`

#### Dữ liệu bridge và switch mới

```python
bridge_ids: tuple[tuple[int, ...], ...] = ()
switch_links: tuple[
    tuple[int, int, tuple[int, ...], str], ...
] = ()
```

- `bridge_ids[row][col]` cho biết ô bridge thuộc bridge nào; `-1` nghĩa là không thuộc bridge.
- Mỗi phần tử `switch_links` có dạng `(row, col, bridge_ids, action)`.
- Dùng tuple để dữ liệu board bất biến.

#### Sửa `is_walkable`

```python
if tile == TileType.BRIDGE:
    bridge_id = self.get_bridge_id(row, col)
    return (
        bridge_id is not None
        and bridge_id < len(bridge_states)
        and bridge_states[bridge_id]
    )
```

Ô bridge chỉ walkable nếu có ID hợp lệ và state tương ứng là `True`.

```python
return tile in {
    TileType.FLOOR,
    TileType.GOAL,
    TileType.SOFT_SWITCH,
    TileType.HEAVY_SWITCH,
    TileType.FRAGILE,
}
```

Hai switch luôn đỡ được block như floor. `FRAGILE` đỡ block khi nằm; `is_block_supported` từ chối trường hợp block đứng trên tile này.

#### Hàm `get_bridge_id`

```python
if not self.bridge_ids or not self.is_inside(row, col):
    return None
```

Không truy cập matrix nếu board không có metadata hoặc tọa độ nằm ngoài board.

```python
bridge_id = self.bridge_ids[row][col]
return bridge_id if bridge_id >= 0 else None
```

Chuyển sentinel `-1` thành `None` cho code gọi dễ kiểm tra.

#### Hàm `get_switch_link`

```python
for switch_row, switch_col, bridge_ids, action in self.switch_links:
    if (row, col) == (switch_row, switch_col):
        return bridge_ids, action
return None
```

Tìm metadata điều khiển bridge từ tọa độ switch.

### 7. `core/level_loader.py`

#### Bổ sung ký hiệu

```python
"S": TileType.SOFT_SWITCH,
"H": TileType.HEAVY_SWITCH,
"B": TileType.BRIDGE,
"F": TileType.FRAGILE,
```

Cho phép bốn ký hiệu mới xuất hiện trong chuỗi board JSON.

#### Khởi tạo metadata bridge

```python
bridges_data = data.get("bridges", [])
bridge_count = len(bridges_data)
```

Level cũ không có `bridges` vẫn hoạt động vì mặc định là danh sách rỗng.

```python
bridge_ids = [
    [-1 for _ in range(len(board_data[0]))]
    for _ in range(len(board_data))
]
```

Tạo matrix cùng kích thước board, ban đầu mọi ô có ID `-1`.

```python
initial_bridge_states = [False] * bridge_count
```

Tạo trạng thái ban đầu cho từng bridge.

#### Đọc từng bridge

```python
for expected_id, bridge_data in enumerate(bridges_data):
    bridge_id = int(bridge_data.get("id", expected_id))
```

Nếu JSON không ghi ID thì dùng vị trí trong danh sách.

```python
if bridge_id != expected_id:
    raise ValueError("Bridge IDs must be consecutive starting at 0")
```

Ép ID liên tục để có thể dùng trực tiếp làm index của `bridge_states`.

```python
initial_bridge_states[bridge_id] = bool(
    bridge_data.get("initially_open", False)
)
```

Đọc trạng thái ban đầu.

Vòng lặp `cells` chuyển từng tọa độ sang integer, kiểm tra nằm trong board, kiểm tra ký hiệu là `B`, sau đó gán `bridge_ids[row][col] = bridge_id`.

Vòng lặp tiếp theo duyệt toàn bộ `tiles` để bảo đảm không có ký hiệu `B` nào thiếu metadata.

#### Đọc switch

```python
switch_links = []
for switch_data in data.get("switches", []):
```

Giữ tương thích với level 1 không có switch.

Code kiểm tra:

- Tọa độ nằm trong board.
- Tọa độ chứa `SOFT_SWITCH` hoặc `HEAVY_SWITCH`.
- Mọi target bridge ID tồn tại.
- Action thuộc `open`, `close`, `toggle`.

```python
switch_links.append((row, col, targets, action))
```

Chuyển JSON động thành tuple metadata được `Board` sử dụng.

#### Tạo Board và initial state

```python
board = Board(
    ...,
    bridge_ids=tuple(tuple(row) for row in bridge_ids),
    switch_links=tuple(switch_links),
)
```

Chuyển list sang tuple để đồng bộ với frozen dataclass.

```python
initial_state = GameState(
    block=start_block,
    bridge_states=tuple(initial_bridge_states),
)
```

State bắt đầu nhận đúng trạng thái bridge từ JSON.

```python
board.is_walkable(row, col, initial_state.bridge_states)
```

Kiểm tra block bắt đầu với bridge state thay vì giả định chỉ có floor.

### 8. `core/transition.py`

#### Sửa `apply_move`

Sau khi tính `moved_block` và kiểm tra support ban đầu, code tạo:

```python
provisional_state = GameState(
    block=moved_block,
    bridge_states=state.bridge_states,
    ...
)
```

Đây là state tạm ở vị trí mới nhưng chưa xử lý switch.

```python
previously_pressed = set(get_activated_switches(board, state))
currently_pressed = set(get_activated_switches(board, provisional_state))
```

Lấy tập switch trước và sau nước đi.

```python
bridge_states = list(state.bridge_states)
```

Chuyển tuple thành list tạm để có thể sửa phần tử.

```python
for row, col in currently_pressed - previously_pressed:
```

Chỉ xử lý switch vừa mới được nhấn.

```python
link = board.get_switch_link(row, col)
if link is None:
    continue
```

Switch không có metadata sẽ không làm thay đổi bridge.

```python
bridge_ids, action = link
for bridge_id in bridge_ids:
```

Một switch có thể điều khiển nhiều bridge.

Ba nhánh `open`, `close`, `toggle` lần lượt gán `True`, `False` hoặc đảo boolean.

```python
next_state = GameState(
    block=moved_block,
    bridge_states=tuple(bridge_states),
    ...
)
```

Tạo state chính thức sau khi switch đã tác động.

```python
if not is_block_supported(board, next_state, moved_block):
    return None
```

Kiểm tra lần hai phòng trường hợp switch đóng bridge ngay dưới block.

#### Hàm `get_activated_switches`

```python
activated: list[tuple[int, int]] = []
block = state.block
```

Tạo kết quả và lấy block từ state.

```python
for row, col in block.occupied_cells():
    tile = board.get_tile(row, col)
```

Duyệt một hoặc hai ô tùy orientation.

```python
if tile == TileType.SOFT_SWITCH:
    activated.append((row, col))
```

Soft switch không kiểm tra orientation.

```python
elif (
    tile == TileType.HEAVY_SWITCH
    and block.orientation == Orientation.STANDING
):
    activated.append((row, col))
```

Heavy switch chỉ được thêm khi block đứng.

```python
return tuple(activated)
```

Trả tuple tọa độ bất biến.

### 9. `game/game.py`

#### Import mới

```python
from ai.astar import solve_astar
from core.enums import Move, TileType
from core.transition import apply_move, get_activated_switches, is_goal_state
```

Controller được nối với solver và switch feedback.

#### Danh sách level

```python
self.level_paths = sorted(self.level_path.parent.glob("*.json"))
self.level_index = self.level_paths.index(self.level_path)
```

Tìm các level cùng thư mục và sắp theo filename để chuyển `01 → 02 → 03`.

#### State autoplay

```python
self.autoplay_moves: list[Move] = []
self.autoplay_generation = 0
```

- `autoplay_moves`: queue bước còn lại.
- `autoplay_generation`: hủy callback cũ sau Restart/load level.

```python
self.board_renderer.sync_with_state(self.state)
```

Áp dụng bridge state ngay khi renderer được tạo, làm bridge đóng bị ẩn.

#### Nút A*

```python
self.astar_button = Button(
    text="A* Auto Play",
    ...,
    on_click=self.start_astar_autoplay,
)
```

Ursina gọi `start_astar_autoplay` khi nhấn nút.

#### `_accept_state`

`try_move` được rút gọn để gọi `_accept_state(next_state)`. Hàm dùng chung này:

- Ghi state mới.
- Tăng move count.
- Đồng bộ block renderer.
- Đồng bộ bridge renderer.
- Phát hiện switch mới được nhấn và hiện thông báo.
- Kiểm tra goal.
- Lập lịch load level tiếp theo sau 1,5 giây.

Tách hàm giúp manual move và autoplay dùng cùng một đường cập nhật UI.

#### `start_astar_autoplay`

```python
if self.has_won or self.is_busy:
    return
```

Không chạy solver khi game đã thắng hoặc đang animation.

```python
result = solve_astar(self.level.board, self.state)
```

Tìm lời giải từ state hiện tại.

Nếu `result.solved=False`, code hiện `A*: No solution`.

Nếu thành công, code copy moves, tăng generation, khóa input, hiển thị cost/expanded nodes và gọi `_play_next_move` sau 0,35 giây.

#### `_play_next_move`

```python
if generation != self.autoplay_generation:
    return
```

Callback cũ tự dừng.

Nếu danh sách move rỗng, `is_busy` được bỏ. Nếu còn move:

```python
move = self.autoplay_moves.pop(0)
next_state = apply_move(self.level.board, self.state, move)
```

Replay vẫn dùng luật game thật. State hợp lệ được chuyển cho `_accept_state`, sau đó bước tiếp theo được lập lịch.

#### `_load_next_level`

Hàm tăng index, load JSON tiếp theo, reset state/count/flags, hủy replay cũ, destroy board renderer, tạo renderer mới, đặt lại block/title/camera/status.

#### Sửa `restart`

Ngoài reset state cũ, Restart hiện còn:

```python
self.autoplay_moves.clear()
self.autoplay_generation += 1
self.board_renderer.sync_with_state(self.state)
```

Nhờ đó replay bị hủy và bridge trở lại trạng thái ban đầu.

### 10. `game/renderer.py`

#### Màu mới

```python
SOFT_SWITCH_COLOR = color.rgb(255, 190, 0)
HEAVY_SWITCH_COLOR = color.rgb(255, 0, 80)
BRIDGE_COLOR = color.rgb(70, 150, 190)
FRAGILE_COLOR = color.rgb(205, 175, 120)
```

Các tile vẫn dùng geometry floor, chỉ đổi màu.

#### Theo dõi entity của bridge

```python
self.bridge_entities: dict[int, list[Entity]] = {}
```

Dictionary nhóm tile và border theo bridge ID để bật/tắt đồng thời.

#### Sửa `_create_tiles`

- `SOFT_SWITCH` gọi `_create_floor(..., SOFT_SWITCH_COLOR)`.
- `HEAVY_SWITCH` gọi `_create_floor(..., HEAVY_SWITCH_COLOR)`.
- `BRIDGE` lấy bridge ID, tạo floor màu xanh và ghi nhận tile cùng các border vừa tạo vào `bridge_entities`.
- `FRAGILE` gọi `_create_floor(..., FRAGILE_COLOR)` để dùng cùng geometry với floor.

```python
border_start = len(self.border_entities)
```

Ghi vị trí danh sách border trước khi tạo bridge tile.

```python
bridge_parts = [tile, *self.border_entities[border_start:]]
```

Lấy đúng tile và bốn border thuộc bridge cell đó.

#### Sửa `_create_floor`

```python
tile_color=FLOOR_COLOR,
create_border: bool = True,
) -> Entity:
```

Hàm nhận màu tùy chọn, có thể bỏ border và trả về Entity vừa tạo. Các thay đổi này cho phép tái sử dụng đúng geometry floor cho switch/bridge.

#### Hàm `sync_with_state`

```python
for bridge_id, entities in self.bridge_entities.items():
```

Duyệt từng nhóm bridge.

```python
is_open = (
    bridge_id < len(state.bridge_states)
    and state.bridge_states[bridge_id]
)
```

Đọc trạng thái an toàn, tránh index ngoài tuple.

```python
for entity in entities:
    entity.enabled = is_open
```

Ẩn cả tile và border khi đóng; hiện toàn bộ khi mở.

### 11. `levels/basic/level_02.json`

File mới tạo level thử soft switch.

```json
"name": "Level 2 - Soft Switch Bridge Lab"
```

Tên được hiển thị trên UI.

`board` là bản đồ 12 cột × 9 hàng, gồm vùng thử nghiệm bên trái, bridge ở giữa và goal bên phải.

```json
"cells": [[3, 6], [3, 7], [4, 6], [4, 7]],
"initially_open": false
```

Bốn ô `B` thuộc bridge 0 và bắt đầu đóng.

```json
"row": 6,
"col": 3,
"bridge_ids": [0],
"action": "open"
```

Soft switch tại `(6,3)` mở bridge 0 vĩnh viễn khi được nhấn.

Start là block đứng tại `(1,1)`. Không gian mở cho phép người chơi thử bridge trước, sau đó quay lại switch.

### 12. `levels/basic/level_03.json`

File mới tạo level thử heavy switch. Cấu trúc bridge, start và goal giống level 2 để chỉ thay đổi biến cần thử.

Khác biệt quan trọng trong board:

```text
.##H##......
```

`H` tại `(6,3)` thay cho `S`. Không gian xung quanh cho phép block nằm ngang/dọc qua `H` mà bridge vẫn đóng, sau đó maneuver để đứng trên `H`.

Metadata switch vẫn dùng `action: open` và điều khiển bridge 0.

### 13. `tests/test_advanced_tiles.py`

File placeholder được thay bằng năm test.

#### `_switch_board`

Tạo board nhỏ 2×1 để unit test switch mà không cần đọc JSON.

#### `test_soft_switch_activates_under_part_of_block`

Đặt block nằm ngang trên soft switch và yêu cầu kết quả chứa `(0,0)`.

#### `test_heavy_switch_does_not_activate_under_lying_block`

Đặt block nằm ngang trên heavy switch và yêu cầu tuple rỗng.

#### `test_heavy_switch_activates_under_standing_block`

Đặt block đứng trên heavy switch và yêu cầu switch được phát hiện.

#### `test_closed_bridge_rejects_block_before_switch_activation`

Load level 2, thực hiện đường đi đến sát bridge, xác nhận `bridge_states == (False,)`, rồi xác nhận move vào bridge trả `None`.

#### `test_lying_on_heavy_switch_does_not_open_bridge`

Load level 3, di chuyển block vào tư thế nằm có chứa ô `(6,3)`, sau đó xác nhận orientation không phải `STANDING` và bridge vẫn đóng.

### 14. `tests/test_level_loader.py`

File placeholder được thay bằng test metadata.

```python
LEVELS = Path(__file__).parents[1] / "levels" / "basic"
```

Tạo đường dẫn độc lập với working directory.

`test_soft_switch_level_loads_bridge_metadata` kiểm tra:

- `S` được chuyển thành `SOFT_SWITCH`.
- `B` được chuyển thành `BRIDGE`.
- Ô bridge ánh xạ đến ID 0.
- Bridge ban đầu đóng.

`test_heavy_switch_level_loads` kiểm tra `H` được chuyển thành `HEAVY_SWITCH`.

### 15. `tests/test_solvers.py`

File placeholder được thay bằng test A*.

#### Helper `_solve`

```python
result = solve_astar(level.board, level.initial_state)
```

Chạy solver.

```python
for move in result.moves:
    next_state = apply_move(level.board, state, move)
    assert next_state is not None
```

Replay lời giải bằng transition thật. Test này không chỉ tin kết quả A* mà còn xác nhận mọi move đều hợp lệ.

Ba test sau xác nhận:

- A* giải được level 1 và `cost == len(moves)` vì level 1 chỉ có floor/goal cost 1.
- A* giải level 2 với bridge cuối cùng mở.
- A* giải level 3 với bridge cuối cùng mở.
- Final state trong cả ba trường hợp đều thỏa `is_goal_state`.
- `get_step_cost` dùng `max` khi block nằm trên hai tile.
- UCS và A* trả cùng chi phí tối ưu trên cả ba level.

### 16. Các file `__pycache__/*.pyc`

Git status đang hiển thị nhiều file `.pyc` thay đổi hoặc mới ở `ai`, `core`, `game` và `tests`. Đây là Python bytecode được interpreter và pytest tạo tự động khi import/chạy test.

Các file này:

- Không chứa source cần giải thích thủ công.
- Không phải một phần thiết kế chức năng.
- Có thể khác nhau giữa Python 3.13 và 3.14.
- Nên được loại khỏi Git bằng `.gitignore` với `__pycache__/` và `*.pyc`.

---

## PHẦN B — GIẢI THÍCH LOGIC VÀ THUẬT TOÁN

## 1. Mục tiêu

Phiên bản ban đầu của dự án mới hỗ trợ bàn chơi cơ bản, block và các phép di chuyển. Phần mở rộng này bổ sung:

- Soft switch (light switch).
- Heavy switch.
- Bridge có trạng thái đóng/mở.
- Hai level riêng để thử nghiệm từng loại switch.
- Tự động chuyển level sau khi thắng.
- Thuật toán A* tìm đường tối ưu.
- Nút `A* Auto Play` tự động thực hiện lời giải.
- Hiển thị switch và bridge trong giao diện 3D.
- Các kiểm thử tự động cho luật chơi và thuật toán.

## 2. Ký hiệu mới trong bản đồ

Level được lưu dưới dạng JSON. Các ký hiệu trên bàn chơi gồm:

| Ký hiệu | Ý nghĩa |
|---|---|
| `.` | Ô trống (void) |
| `#` | Sàn bình thường |
| `G` | Ô đích |
| `S` | Soft switch |
| `H` | Heavy switch |
| `B` | Bridge |

Các ký hiệu `S`, `H` và `B` được ánh xạ sang `TileType` trong `core/level_loader.py`.

## 3. Cấu trúc khai báo switch và bridge

Ngoài mảng `board`, level JSON có thêm hai danh sách `bridges` và `switches`.

Ví dụ:

```json
{
  "bridges": [
    {
      "id": 0,
      "cells": [[3, 6], [3, 7]],
      "initially_open": false
    }
  ],
  "switches": [
    {
      "row": 6,
      "col": 3,
      "bridge_ids": [0],
      "action": "open"
    }
  ]
}
```

Mỗi bridge có:

- `id`: mã số bridge.
- `cells`: các ô thuộc bridge.
- `initially_open`: trạng thái ban đầu.

Mỗi switch có:

- Vị trí `row`, `col`.
- Danh sách `bridge_ids` mà switch điều khiển.
- `action`: hành động `open`, `close` hoặc `toggle`.

Loader kiểm tra ID bridge, tọa độ, ký hiệu trên bàn, switch trỏ đến bridge hợp lệ và hành động được hỗ trợ.

## 4. Trạng thái bridge

Trạng thái đóng/mở của bridge được lưu trong `GameState`:

```python
bridge_states: tuple[bool, ...]
```

Ví dụ `(False, True)` nghĩa là bridge 0 đang đóng và bridge 1 đang mở.

Việc lưu bridge trong `GameState` có hai lợi ích:

1. Game có thể khôi phục chính xác toàn bộ trạng thái sau mỗi bước.
2. A* có thể phân biệt cùng một vị trí block nhưng bridge có trạng thái khác nhau.

## 5. Luật soft switch

Soft switch được kích hoạt khi bất kỳ phần nào của block chạm vào nó.

```python
soft_active = any(
    board.get_tile(row, col) == TileType.SOFT_SWITCH
    for row, col in block.occupied_cells()
)
```

Do đó soft switch hoạt động khi block:

- Đứng trên switch.
- Nằm ngang và một trong hai phần chạm switch.
- Nằm dọc và một trong hai phần chạm switch.

## 6. Luật heavy switch

Heavy switch chỉ được kích hoạt khi block đứng thẳng hoàn toàn trên switch.

```python
heavy_active = (
    block.orientation == Orientation.STANDING
    and board.get_tile(block.row, block.col)
        == TileType.HEAVY_SWITCH
)
```

Nếu block nằm ngang hoặc nằm dọc qua heavy switch, bridge vẫn đóng.

## 7. Luật bridge

- Bridge đóng không thể đỡ block.
- Di chuyển lên bridge đang đóng là nước đi không hợp lệ.
- Bridge đóng được ẩn khỏi giao diện.
- Khi switch được kích hoạt, trạng thái bridge thay đổi theo `action`.
- Bridge mở xuất hiện trên bàn và đỡ block giống sàn bình thường.

Quy trình xử lý một nước đi:

```text
Tính vị trí block mới
        ↓
Kiểm tra vị trí bằng trạng thái bridge hiện tại
        ↓
Phát hiện switch vừa được nhấn
        ↓
Cập nhật bridge_states
        ↓
Tạo GameState mới
        ↓
Kiểm tra lại khả năng đỡ block
        ↓
Chấp nhận hoặc từ chối nước đi
```

Chỉ switch mới được nhấn mới thực hiện hành động. Điều này tránh trường hợp `toggle` liên tục đổi trạng thái khi block vẫn còn nằm trên switch.

## 8. Thiết kế level

### Level 1

`levels/basic/level_01.json` được giữ nguyên, dùng để thử luật di chuyển Bloxorz cơ bản.

### Level 2 – Soft Switch Bridge Lab

Level 2 có một vùng di chuyển rộng, soft switch, bridge đang đóng và vùng đích phía bên kia bridge.

Người chơi có thể:

- Đi đến bridge trước khi kích hoạt switch.
- Kiểm tra rằng block không thể đi lên bridge đang đóng.
- Quay lại soft switch.
- Nằm một phần block lên switch để mở bridge.
- Đi qua bridge và đến goal.

### Level 3 – Heavy Switch Bridge Lab

Level 3 có bố cục thử nghiệm tương tự nhưng sử dụng heavy switch.

Người chơi có thể:

- Nằm block qua heavy switch và quan sát bridge vẫn đóng.
- Di chuyển xung quanh switch để thay đổi orientation.
- Đứng thẳng trên heavy switch để mở bridge.
- Đi qua bridge và hoàn thành level.

## 9. Tự động chuyển level

Game đọc các file JSON trong thư mục level theo thứ tự tên:

```text
level_01.json → level_02.json → level_03.json
```

Sau khi thắng:

1. Hiển thị thông báo thắng và số bước.
2. Chờ 1,5 giây.
3. Hủy renderer của bàn cũ.
4. Nạp level tiếp theo.
5. Đặt lại state, số bước và camera.

Sau level cuối, game giữ màn hình chiến thắng vì không còn level tiếp theo.

## 10. Thuật toán A*

A* tìm lời giải có số lần lăn block nhỏ nhất.

### 10.1 Chi phí

Chi phí được xác định bởi loại tile trong state đích:

```text
FLOOR / GOAL / BRIDGE = 1
SWITCH ACTIVATION (bridge state thay đổi) = 2
FRAGILE = 5
g(n) = tổng chi phí tile từ trạng thái bắt đầu đến n
```

Khi block nằm trên hai ô, step cost là giá trị lớn nhất của hai ô. Orientation không tự tạo phụ phí.

### 10.2 Heuristic

Heuristic dùng khoảng cách Manhattan nhỏ nhất từ một ô block đang chiếm đến goal:

```python
distance = min(
    abs(row - goal_row) + abs(col - goal_col)
    for row, col in state.block.occupied_cells()
)

h(n) = ceil(distance / 2) * MINIMUM_STEP_COST
```

Chia cho 2 vì một lần lăn có thể làm block tiến tối đa hai ô.

### 10.3 Hàm đánh giá

```text
f(n) = g(n) + h(n)
```

Heuristic bỏ qua vật cản, switch, bridge và yêu cầu block phải đứng ở goal. Vì vậy nó có thể đánh giá thấp nhưng không đánh giá cao chi phí thật, phù hợp để A* tìm lời giải tối ưu.

### 10.4 Quản lý trạng thái

A* lưu chi phí tốt nhất cho mỗi `GameState`. Khóa trạng thái bao gồm:

- Vị trí block.
- Orientation của block.
- Trạng thái các bridge.
- Các trường dành cho split block trong tương lai.

Priority queue sắp xếp node theo `f = g + h`. Một bộ đếm phụ được dùng để tránh Python phải so sánh trực tiếp hai `GameState` khi priority bằng nhau.

## 11. A* Auto Play

Nút `A* Auto Play` được thêm bên cạnh nút Restart.

Khi nhấn nút:

1. A* tìm đường từ trạng thái hiện tại.
2. Giao diện hiển thị số bước và số node đã mở rộng.
3. Điều khiển thủ công tạm thời bị khóa.
4. Các bước được thực hiện tự động sau mỗi 0,35 giây.
5. Mỗi bước vẫn gọi cùng hàm `apply_move()` như chế độ thủ công.
6. Renderer cập nhật bridge sau từng bước.
7. Khi đến goal, quy trình thắng và chuyển level bình thường được sử dụng.

Restart sẽ hủy chuỗi autoplay hiện tại để các callback cũ không tiếp tục di chuyển block sau khi reset.

## 12. Hiển thị

Switch và bridge dùng cùng hình dạng, kích thước và đường viền với floor. Chúng chỉ khác màu:

| Đối tượng | Cách hiển thị |
|---|---|
| Floor | Xám |
| Soft switch | Cam |
| Heavy switch | Đỏ/hồng sáng |
| Bridge mở | Xanh dương |
| Bridge đóng | Ẩn |
| Goal | Đen |

Tile và toàn bộ đường viền bridge được bật/tắt cùng nhau để bridge đóng không để lại viền trên màn hình.

## 13. Các file chính đã thay đổi

| File | Nội dung |
|---|---|
| `core/board.py` | Walkability của switch/bridge và ánh xạ bridge ID |
| `core/level_loader.py` | Đọc `S`, `H`, `B` và metadata |
| `core/transition.py` | Kích hoạt switch và cập nhật bridge |
| `ai/heuristics.py` | Heuristic Manhattan cho Bloxorz |
| `ai/astar.py` | Thuật toán A* |
| `ai/result.py` | Cấu trúc kết quả tìm kiếm |
| `game/renderer.py` | Màu switch và hiển thị bridge |
| `game/game.py` | Chuyển level và A* Auto Play |
| `levels/basic/level_02.json` | Level thử soft switch |
| `levels/basic/level_03.json` | Level thử heavy switch |
| `tests/test_advanced_tiles.py` | Kiểm thử switch và bridge |
| `tests/test_level_loader.py` | Kiểm thử đọc level |
| `tests/test_solvers.py` | Kiểm thử A* trên ba level |

## 14. Kết quả kiểm thử

Các trường hợp đã được kiểm tra:

- Soft switch hoạt động khi block nằm.
- Heavy switch không hoạt động khi block nằm.
- Heavy switch hoạt động khi block đứng.
- Bridge đóng từ chối block trước khi switch được kích hoạt.
- Metadata switch và bridge được nạp đúng.
- A* giải được level gốc.
- A* mở bridge và giải được level soft switch.
- A* đứng trên heavy switch, mở bridge và giải được level heavy switch.

Kết quả cuối:

```text
16 passed
```

## 15. Giới hạn hiện tại

- Level 2 và 3 chỉ minh họa hành động `open`; chưa có level riêng cho `close` và `toggle`.
- A* chạy đồng bộ trước khi bắt đầu animation.
- Chưa có Pause, Resume hoặc Step cho autoplay.
- Chưa cài đặt di chuyển split block.
- Các file `__pycache__` và `*.pyc` nên được loại khỏi Git bằng `.gitignore`.

## 16. Giải thích chi tiết code thuật toán A*

Phần này phân tích trực tiếp code trong `ai/astar.py`, thay vì chỉ mô tả luật trò chơi.

### 16.1 Các import ở dòng 3–11

```python
from heapq import heappop, heappush
from itertools import count
```

- `heappush()` thêm một phần tử vào min-heap.
- `heappop()` lấy phần tử có tuple nhỏ nhất ra khỏi heap.
- `count()` tạo dãy số `0, 1, 2, ...` dùng để phá hòa khi hai node có cùng priority.

```python
from ai.heuristics import goal_distance
from ai.result import SearchResult
from core.board import Board
from core.enums import Move
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state
```

- `goal_distance`: tính `h(n)`.
- `SearchResult`: đóng gói lời giải trả về cho UI.
- `Board`: bàn chơi tĩnh.
- `Move`: bốn hành động `UP`, `DOWN`, `LEFT`, `RIGHT`.
- `GameState`: trạng thái đầy đủ của bài toán.
- `get_valid_moves`: sinh successor hợp lệ.
- `is_goal_state`: kiểm tra block đứng trên goal.

### 16.2 Hàm `_reconstruct_moves`, dòng 14–25

```python
def _reconstruct_moves(
    parents: dict[GameState, tuple[GameState, Move]],
    state: GameState,
) -> tuple[Move, ...]:
```

`parents` có dạng:

```text
trạng thái con → (trạng thái cha, hành động từ cha đến con)
```

Ví dụ:

```text
S2 → (S1, RIGHT)
S1 → (S0, DOWN)
```

Tham số `state` ban đầu là goal state.

```python
moves: list[Move] = []
```

Tạo danh sách rỗng để chứa các bước truy ngược từ goal về start.

```python
while state in parents:
```

Trạng thái ban đầu không có cha nên không nằm trong `parents`. Vòng lặp dừng khi truy ngược đến initial state.

```python
state, move = parents[state]
```

Lấy cha của state hiện tại và hành động đã tạo ra state hiện tại. Sau câu lệnh này, biến `state` được cập nhật thành state cha.

```python
moves.append(move)
```

Thêm hành động vào danh sách. Vì đang đi từ goal về start nên thứ tự hiện tại bị ngược.

```python
moves.reverse()
```

Đảo danh sách thành thứ tự đúng từ start đến goal.

```python
return tuple(moves)
```

Trả về tuple bất biến, phù hợp với `SearchResult`.

### 16.3 Khởi tạo A*, dòng 28–35

```python
def solve_astar(board: Board, initial_state: GameState) -> SearchResult:
```

Hàm nhận bàn chơi và trạng thái hiện tại. Vì vậy người chơi có thể nhấn A* ngay từ giữa level, không bắt buộc phải Restart.

```python
sequence = count()
```

Tạo tie-breaker. Heap chứa tuple và Python so sánh tuple từ trái sang phải. Nếu `f` và `g` bằng nhau, `sequence` bảo đảm hai phần tử vẫn khác nhau trước khi Python phải so sánh `GameState`.

```python
frontier: list[tuple[int, int, int, GameState]] = []
```

Khai báo priority queue. Mỗi phần tử có dạng:

```text
(f, g, sequence_number, state)
```

Trong đó:

- `f = g + h`: độ ưu tiên của A*.
- `g`: chi phí thật từ start.
- `sequence_number`: phá hòa.
- `state`: trạng thái cần xét.

```python
best_cost: dict[GameState, int] = {initial_state: 0}
```

`best_cost[state]` lưu `g` nhỏ nhất đã tìm được cho state đó. Initial state có chi phí 0.

Dictionary này đồng thời thay vai trò của bảng khoảng cách trong Dijkstra và A*.

```python
parents: dict[GameState, tuple[GameState, Move]] = {}
```

Lưu đường đi tốt nhất hiện tại để cuối cùng dựng lại chuỗi hành động.

```python
expanded_nodes = 0
```

Đếm số state đã được lấy ra và mở rộng successor. Giá trị này được hiển thị trên UI để đánh giá hiệu năng.

### 16.4 Đưa initial state vào heap, dòng 37–40

```python
heappush(
    frontier,
    (goal_distance(board, initial_state), 0, next(sequence), initial_state),
)
```

Ở initial state:

```text
g(start) = 0
f(start) = 0 + h(start) = h(start)
```

`next(sequence)` trả về 0 trong lần gọi đầu tiên.

### 16.5 Vòng lặp chính, dòng 42–46

```python
while frontier:
```

A* tiếp tục khi còn state chưa xét. Nếu heap rỗng mà chưa tìm thấy goal thì bài toán không có lời giải.

```python
_, cost, _, state = heappop(frontier)
```

Lấy node có `f` nhỏ nhất. Hai dấu `_` cho biết code không cần dùng lại `f` và sequence number sau khi pop.

`cost` chính là `g` của entry vừa lấy ra.

```python
if cost != best_cost.get(state):
    continue
```

Đây là cơ chế bỏ qua entry cũ trong heap.

Ví dụ:

1. A* tìm thấy state `X` với `g = 10` và push vào heap.
2. Sau đó tìm thấy đường tốt hơn đến `X` với `g = 7` và push thêm entry mới.
3. `best_cost[X]` được đổi thành 7.
4. Khi entry cũ `g = 10` được pop, `10 != 7`, nên entry đó bị bỏ qua.

Python `heapq` không có thao tác giảm priority trực tiếp. Cho phép nhiều entry và bỏ qua entry cũ là cách cài đặt phổ biến, đơn giản và chính xác.

### 16.6 Kiểm tra goal, dòng 48–50

```python
if is_goal_state(board, state):
```

Chỉ kiểm tra goal sau khi state được pop khỏi priority queue, không dừng ngay khi vừa sinh ra goal.

Điểm này quan trọng: goal vừa được sinh ra chưa chắc đã đi bằng đường có chi phí nhỏ nhất. Với heuristic admissible/consistent, goal được pop mới bảo đảm có chi phí tối ưu.

```python
moves = _reconstruct_moves(parents, state)
```

Truy ngược bảng `parents` để lấy danh sách hành động.

```python
return SearchResult(moves, cost, expanded_nodes)
```

Trả về:

- Chuỗi move.
- Tổng chi phí `g`.
- Số node đã mở rộng.
- `solved=True` dùng giá trị mặc định.

### 16.7 Mở rộng successor, dòng 52–58

```python
expanded_nodes += 1
```

State hiện tại không phải goal và sắp được mở rộng nên tăng bộ đếm.

```python
for move, next_state in get_valid_moves(board, state):
```

`get_valid_moves` thử bốn hướng và chỉ trả về nước đi hợp lệ. Nó đã xử lý:

- Hình học block.
- Void và biên board.
- Bridge đóng/mở.
- Soft switch.
- Heavy switch.

Do đó A* không chứa luật game riêng; A* chỉ làm việc trên graph do transition model cung cấp.

```python
next_cost = cost + get_step_cost(board, state, next_state)
```

Chi phí của lần lăn được lấy từ terrain của `next_state`, nên:

```text
g(next) = g(current) + step_cost(next_state)
```

```python
if next_cost >= best_cost.get(next_state, float("inf")):
    continue
```

- Nếu chưa thấy `next_state`, `.get()` trả về vô cực và đường mới được chấp nhận.
- Nếu đã có đường rẻ hơn hoặc bằng, successor bị bỏ qua.
- Chỉ đường có `g` nhỏ hơn mới cập nhật state.

Dùng `>=` thay vì `>` giúp tránh push lại cùng một state với cùng chi phí, giảm số node dư thừa.

### 16.8 Cập nhật đường tốt hơn, dòng 60–66

```python
best_cost[next_state] = next_cost
```

Ghi nhận chi phí tốt nhất mới.

```python
parents[next_state] = (state, move)
```

Ghi nhận rằng đường tốt nhất hiện tại đến `next_state` đi từ `state` bằng `move`.

Nếu sau này có đường tốt hơn nữa, cả `best_cost` và `parents` đều bị ghi đè để phản ánh đường mới.

```python
priority = next_cost + goal_distance(board, next_state)
```

Tính:

```text
priority = f(next) = g(next) + h(next)
```

```python
heappush(
    frontier,
    (priority, next_cost, next(sequence), next_state),
)
```

Đưa successor vào heap. Vì heap là min-heap, node có `f` thấp nhất sẽ được xét trước.

Tuple còn dùng `next_cost` làm tie-breaker thứ nhất. Khi hai node có cùng `f`, code ưu tiên node có `g` nhỏ hơn; sau đó mới dùng sequence number.

### 16.9 Không tìm được lời giải, dòng 68

```python
return SearchResult.no_solution(expanded_nodes)
```

Dòng này chỉ chạy khi `frontier` đã rỗng. Nghĩa là mọi state có thể đạt được đều đã được xét nhưng không có goal.

Kết quả có:

```text
moves = ()
cost = 0
expanded_nodes = số node đã mở rộng
solved = False
```

## 17. Giải thích chi tiết heuristic

Code nằm trong `ai/heuristics.py`.

```python
from math import ceil
```

Import hàm làm tròn lên. Ví dụ `ceil(5 / 2) = 3`.

```python
goal_row, goal_col = board.find_goal()
```

Tìm tọa độ duy nhất của goal trên board.

```python
distance = min(
    abs(row - goal_row) + abs(col - goal_col)
    for row, col in state.block.occupied_cells()
)
```

`occupied_cells()` trả về:

- Một ô nếu block đứng.
- Hai ô nếu block nằm ngang hoặc dọc.

Code tính Manhattan distance từ từng ô block đến goal rồi lấy khoảng cách nhỏ nhất.

Ví dụ block nằm ở `(2, 3)` và `(2, 4)`, goal ở `(6, 7)`:

```text
d1 = |2-6| + |3-7| = 8
d2 = |2-6| + |4-7| = 7
distance = min(8, 7) = 7
```

```python
return ceil(distance / 2)
```

Một lần lăn có thể đưa đầu block tiến tối đa hai ô, nên số bước ít nhất không thể thấp hơn `ceil(distance / 2)`.

Trong ví dụ:

```text
h = ceil(7 / 2) = 4
```

Heuristic không cộng chi phí đi vòng đến switch và không xét bridge đang đóng. Do đó nó có thể nhỏ hơn nhiều so với chi phí thật, nhưng không cố tình cộng quá mức. A* vẫn tìm lời giải tối ưu; nhược điểm là có thể mở rộng nhiều node hơn một heuristic mạnh hơn.

## 18. Giải thích `SearchResult`

Code nằm trong `ai/result.py`.

```python
@dataclass(frozen=True)
class SearchResult:
```

- `@dataclass` tự sinh constructor và các hàm tiện ích.
- `frozen=True` làm kết quả bất biến sau khi tạo.

```python
moves: tuple[Move, ...]
```

Chuỗi hành động từ trạng thái hiện tại đến goal.

```python
cost: int
```

Tổng chi phí. Với phiên bản hiện tại, nó bằng số move.

```python
expanded_nodes: int
```

Số node A* đã mở rộng.

```python
solved: bool = True
```

Cho biết có tìm thấy lời giải hay không. Kết quả thành công không cần truyền lại `True` vì đã có mặc định.

```python
@classmethod
def no_solution(cls, expanded_nodes: int) -> "SearchResult":
    return cls((), 0, expanded_nodes, False)
```

Factory method tạo kết quả thất bại thống nhất, tránh lặp constructor ở solver.

## 19. Vì sao `GameState` dùng được làm khóa dictionary

`GameState` và `Block` là frozen dataclass. Các trường được dùng đều là kiểu hashable như enum, integer và tuple. Vì vậy có thể dùng trực tiếp:

```python
best_cost: dict[GameState, int]
parents: dict[GameState, tuple[GameState, Move]]
```

Hai state chỉ bằng nhau khi toàn bộ dữ liệu bằng nhau. Đặc biệt:

```text
block giống nhau + bridge_states=(False,)
```

khác với:

```text
block giống nhau + bridge_states=(True,)
```

Nếu bỏ `bridge_states` khỏi khóa, A* có thể loại nhầm state sau khi switch đã mở bridge và kết luận level không có lời giải.

## 20. Liên kết giữa A* và transition model

Code A* gọi:

```python
for move, next_state in get_valid_moves(board, state):
```

Trong `core/transition.py`, `get_valid_moves` thực hiện:

```python
successors = []

for move in Move:
    next_state = apply_move(board, state, move)

    if next_state is not None:
        successors.append((move, next_state))
```

Giải thích:

1. `for move in Move` duyệt bốn hướng.
2. `apply_move` trả về state mới hoặc `None`.
3. Chỉ state khác `None` mới được thêm vào successor.
4. A* không bao giờ mở rộng một nước đi làm block rơi hoặc đi lên bridge đóng.

Thiết kế này bảo đảm manual play và A* sử dụng cùng một bộ luật, tránh trường hợp AI tìm ra đường mà game không thực hiện được.

## 21. Giải thích code cập nhật switch trong `apply_move`

```python
moved_block = calculate_moved_block(state.block, move)
```

Tính block mới dựa trên orientation và hướng đi.

```python
if not is_block_supported(board, state, moved_block):
    return None
```

Kiểm tra block mới trên board với bridge state hiện tại. Nếu block rơi hoặc chạm bridge đóng, nước đi bị loại.

```python
provisional_state = GameState(
    block=moved_block,
    bridge_states=state.bridge_states,
    ...
)
```

Tạo state tạm thời để kiểm tra switch tại vị trí mới, trước khi cập nhật bridge.

```python
previously_pressed = set(get_activated_switches(board, state))
currently_pressed = set(get_activated_switches(board, provisional_state))
```

Tạo hai tập hợp switch: trước và sau nước đi.

```python
for row, col in currently_pressed - previously_pressed:
```

Hiệu hai tập hợp chỉ giữ switch vừa mới được nhấn.

```python
link = board.get_switch_link(row, col)
```

Lấy bridge ID và action liên kết với switch.

```python
bridge_states = list(state.bridge_states)
```

Chuyển tuple bất biến thành list để cập nhật.

```python
if action == "open":
    bridge_states[bridge_id] = True
elif action == "close":
    bridge_states[bridge_id] = False
else:
    bridge_states[bridge_id] = not bridge_states[bridge_id]
```

Cài đặt ba hành động. Nhánh `else` tương ứng `toggle` vì loader đã loại mọi action không hợp lệ.

```python
next_state = GameState(
    block=moved_block,
    bridge_states=tuple(bridge_states),
    ...
)
```

Đóng gói list trở lại tuple và tạo state chính thức.

```python
if not is_block_supported(board, next_state, moved_block):
    return None
```

Kiểm tra lần hai sau khi switch thay đổi bridge. Bước này cần thiết cho action `close` hoặc `toggle`, vì switch có thể đóng một bridge đang đỡ block.

## 22. Giải thích code A* Auto Play

Trong `game/game.py`:

```python
result = solve_astar(self.level.board, self.state)
```

Solver bắt đầu từ state hiện tại của người chơi.

```python
if not result.solved:
    self._show_temporary_message("A*: No solution")
    return
```

Không chạy replay nếu frontier đã cạn mà không có goal.

```python
self.autoplay_moves = list(result.moves)
```

Chuyển tuple thành list để có thể lấy từng bước.

```python
self.autoplay_generation += 1
generation = self.autoplay_generation
```

Mỗi replay có mã phiên riêng. Restart hoặc load level tăng mã này, làm callback từ phiên cũ mất hiệu lực.

```python
self.is_busy = True
```

Khóa manual input trong lúc autoplay.

```python
invoke(self._play_next_move, generation, delay=0.35)
```

Ursina gọi bước đầu sau 0,35 giây để người dùng nhìn thấy animation theo từng bước.

Trong `_play_next_move`:

```python
if generation != self.autoplay_generation:
    return
```

Dừng callback cũ sau Restart hoặc chuyển level.

```python
move = self.autoplay_moves.pop(0)
next_state = apply_move(self.level.board, self.state, move)
```

Lấy bước tiếp theo và chạy qua đúng transition model của game.

```python
self._accept_state(next_state)
```

Cập nhật block renderer, bridge renderer, move count, thông báo switch và kiểm tra chiến thắng.

```python
if not self.has_won:
    invoke(self._play_next_move, generation, delay=0.35)
```

Lập lịch bước tiếp theo cho đến khi goal được đạt.

## 23. Độ phức tạp của A*

Gọi `V` là số state có thể đạt được và `E` là số transition hợp lệ.

- Mỗi state có tối đa 4 successor nên `E ≤ 4V`.
- Mỗi thao tác heap có độ phức tạp `O(log V)`.
- Thời gian xấp xỉ `O(E log V)` trong phạm vi graph được A* khám phá.
- Bộ nhớ là `O(V)` cho heap, `best_cost` và `parents`.

Số state không chỉ phụ thuộc số ô. Một vị trí có thể có ba orientation và nhiều tổ hợp bridge state. Với `k` bridge độc lập, riêng bridge có thể tạo tối đa `2^k` tổ hợp. Vì vậy việc dùng heuristic để giảm số state mở rộng rất quan trọng khi level lớn hơn.
