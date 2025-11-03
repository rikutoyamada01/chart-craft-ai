import { Box, Button, Heading, Image, Text, Textarea } from "@chakra-ui/react"
import { useState } from "react"
import useCustomToast from "../hooks/useCustomToast"

export default function HomePage() {
  const [prompt, setPrompt] = useState<string>("")
  const [result, setResult] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const { showErrorToast } = useCustomToast()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!prompt.trim()) {
      showErrorToast("プロンプトを入力してください。")
      return
    }

    setIsLoading(true)
    setResult("")

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/circuits/generate-and-render",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: prompt }),
        },
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const svg = await response.text()
      console.log("SVG response text:", svg)
      const svgDataUrl = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
      setResult(svgDataUrl)
    } catch (error) {
      console.error("API呼び出し中にエラーが発生しました:", error)
      showErrorToast("回路図の生成に失敗しました。")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      minH="100vh"
      bg="gray.100"
      p={8}
    >
      <Heading as="h1" size="xl" color="gray.800" mb={6}>
        Circuit Craft AI
      </Heading>
      <Text fontSize="lg" color="gray.600" mb={8}>
        作りたい回路を文章で説明してください
      </Text>

      <Box
        as="form"
        onSubmit={handleSubmit}
        w="full"
        maxW="2xl"
        bg="white"
        p={6}
        borderRadius="lg"
        boxShadow="md"
      >
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 1.5Vの乾電池と330Ωの抵抗、赤色LEDを直列に接続してください。"
          disabled={isLoading}
          size="lg"
          height="160px"
        />
        <Button
          type="submit"
          w="full"
          mt={4}
          colorScheme="blue"
          loading={isLoading}
          loadingText="生成中..."
        >
          回路図を生成
        </Button>
      </Box>

      {result && (
        <Box
          w="full"
          maxW="2xl"
          mt={8}
          bg="white"
          p={6}
          borderRadius="lg"
          boxShadow="md"
        >
          <Heading as="h2" size="lg" color="gray.800" mb={4}>
            生成結果 (SVG)
          </Heading>
          <Box border="1px" borderColor="gray.200" borderRadius="md" p={4}>
            <Image src={result} />
          </Box>
        </Box>
      )}
    </Box>
  )
}
