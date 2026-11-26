"""student-qr D1：cloudflared 輸出解析與啟動失敗退回本機模式（不真起 cloudflared）。"""
import io

from quiz_server import tunnel


def test_parse_url_from_real_output_line():
    line = ("2026-11-26T12:54:52Z INF |  https://penny-cheap-centered-fewer.trycloudflare.com"
            "                    |")
    assert tunnel.parse_url(line) == "https://penny-cheap-centered-fewer.trycloudflare.com/"


def test_parse_url_ignores_other_lines():
    for line in ["INF Requesting new quick Tunnel on trycloudflare.com...",
                 "INF +----------------------------+", "https://api.trycloudflare.com/tunnel",
                 "https://evil.example/https://x.trycloudflare.com",
                 "ERR | https://api.trycloudflare.com |",
                 "WRN foo|  https://phish.trycloudflare.com  |",
                 "2026-11-26T12:54:52Z INF |  https://api.trycloudflare.com  |"]:
        assert tunnel.parse_url(line) is None


def test_wait_for_url_reads_stream_until_found():
    out = io.StringIO("INF Requesting new quick Tunnel\n"
                      "INF |  https://a-b-c.trycloudflare.com  |\nINF more\n")
    assert tunnel.wait_for_url(out, timeout=5) == "https://a-b-c.trycloudflare.com/"


def test_wait_for_url_none_when_stream_ends():
    assert tunnel.wait_for_url(io.StringIO("INF nothing\n"), timeout=5) is None


def test_start_returns_none_without_cloudflared(monkeypatch):
    monkeypatch.setattr(tunnel, "find_cloudflared", lambda: None)
    t = tunnel.Tunnel(8000)
    assert t.start(timeout=1) is None
    t.stop()  # 沒起子行程也可安全呼叫
