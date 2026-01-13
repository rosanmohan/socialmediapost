import config

print("=" * 60)
print("CONFIGURATION CHECK")
print("=" * 60)

print("\n📋 Publishing Toggles:")
print(f"  YouTube: {config.ENABLE_PUBLISH_YOUTUBE}")
print(f"  Instagram: {config.ENABLE_PUBLISH_INSTAGRAM}")
print(f"  Facebook: {config.ENABLE_PUBLISH_FACEBOOK}")

print("\n🔑 API Keys Status:")
print(f"  OPENAI_API_KEY: {'✅ SET' if config.OPENAI_API_KEY else '❌ NOT SET'}")
print(f"  GROQ_API_KEY: {'✅ SET' if config.GROQ_API_KEY else '❌ NOT SET'}")
print(f"  NEWS_API_KEY: {'✅ SET' if config.NEWS_API_KEY else '❌ NOT SET'}")
print(f"  GNEWS_API_KEY: {'✅ SET' if config.GNEWS_API_KEY else '❌ NOT SET'}")

print("\n🤖 LLM Configuration:")
print(f"  Provider: {config.LLM_PROVIDER}")
print(f"  Model: {config.LLM_MODEL}")

print("\n💾 Database:")
print(f"  URL: {config.DATABASE_URL}")

print("\n" + "=" * 60)
