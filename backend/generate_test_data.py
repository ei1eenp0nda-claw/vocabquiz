#!/usr/bin/env python3
"""
ProteinHub Test Data Generator
生成测试用的笔记数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db, User, Note, Like, Favorite, Comment
from datetime import datetime, timedelta
import random


def generate_test_data():
    """生成测试数据"""
    engine, Session = init_db('sqlite:///proteinhub.db')
    session = Session()
    
    print("生成测试数据...")
    
    # 创建测试用户
    users = []
    for i in range(5):
        user = User(
            username=f"researcher_{i+1}",
            email=f"researcher{i+1}@proteinhub.com"
        )
        user.set_password("test123")
        session.add(user)
        users.append(user)
    
    session.commit()
    print(f"✅ 创建了 {len(users)} 个测试用户")
    
    # 创建测试笔记 (模拟164篇笔记中的一部分)
    notes_data = [
        {
            "title": "蛋白质结构预测的最新进展",
            "content": "近年来，AlphaFold等深度学习模型在蛋白质结构预测领域取得了突破性进展...",
            "tags": '["蛋白质", "深度学习", "AlphaFold"]',
            "view_count": random.randint(100, 1000)
        },
        {
            "title": "CRISPR基因编辑技术的临床应用",
            "content": "CRISPR-Cas9技术自问世以来，已经在多种遗传疾病的治疗中展现出巨大潜力...",
            "tags": '["CRISPR", "基因编辑", "临床应用"]',
            "view_count": random.randint(100, 1000)
        },
        {
            "title": "单细胞测序技术解析",
            "content": "单细胞RNA测序技术使我们能够在单个细胞水平上研究基因表达...",
            "tags": '["单细胞测序", "转录组", "生物信息学"]',
            "view_count": random.randint(100, 1000)
        },
        {
            "title": "mRNA疫苗的设计与优化",
            "content": "COVID-19疫情推动了mRNA疫苗技术的快速发展，本文探讨其设计原理...",
            "tags": '["mRNA疫苗", "免疫学", "药物设计"]',
            "view_count": random.randint(100, 1000)
        },
        {
            "title": "质谱技术在蛋白质组学中的应用",
            "content": "质谱技术是现代蛋白质组学研究的核心工具，能够高通量鉴定蛋白质...",
            "tags": '["质谱", "蛋白质组学", "分析技术"]',
            "view_count": random.randint(100, 1000)
        }
    ]
    
    notes = []
    for data in notes_data:
        note = Note(
            user_id=random.choice(users).id,
            title=data["title"],
            content=data["content"],
            summary=data["content"][:50] + "...",
            tags=data["tags"],
            view_count=data["view_count"],
            status='published',
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        session.add(note)
        notes.append(note)
    
    session.commit()
    print(f"✅ 创建了 {len(notes)} 篇测试笔记")
    
    # 添加点赞和收藏
    for note in notes:
        # 随机点赞
        for user in random.sample(users, random.randint(0, len(users))):
            if user.id != note.user_id:
                like = Like(user_id=user.id, note_id=note.id)
                session.add(like)
        
        # 随机收藏
        for user in random.sample(users, random.randint(0, len(users)//2)):
            if user.id != note.user_id:
                favorite = Favorite(user_id=user.id, note_id=note.id)
                session.add(favorite)
        
        # 添加评论
        for _ in range(random.randint(0, 3)):
            comment = Comment(
                user_id=random.choice(users).id,
                note_id=note.id,
                content=f"非常有价值的分享！感谢作者。{random.randint(1, 100)}"
            )
            session.add(comment)
    
    session.commit()
    print("✅ 添加了点赞、收藏和评论数据")
    
    session.close()
    print("\n测试数据生成完成！")
    print("可以使用以下命令启动服务器:")
    print("  python app.py")


if __name__ == '__main__':
    generate_test_data()
